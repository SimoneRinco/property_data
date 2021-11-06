from pdata.req.prices import Prices
import pdata.db.utils as db_utils
from pdata.postcode import Postcodes

import pandas

from collections import namedtuple
import datetime
import sqlite3
import os
import datetime

class PricesDb(object):

  Row = namedtuple('Row',
                   ['postcode_district',
                    'postcode',
                    'lat',
                    'lng',
                    'bedrooms',
                    'ptype',
                    'date_added',
                    'price_added',
                    'date_price_changed',
                    'date_removed',
                    'price'
                    ])

  @staticmethod
  def row_from_db_row(db_row):
    return PricesDb.Row(*db_row)

  @staticmethod
  def row_from_prices_raw_item(raw_item):
    lat, lng = db_utils.latlng2int(raw_item.coordinates)
    return PricesDb.Row(
      postcode_district=None,
      postcode=None,
      lat=lat,
      lng=lng, 
      bedrooms=raw_item.bedrooms,
      ptype=db_utils.ptype2int(raw_item.ptype),
      date_added=None,
      price_added=raw_item.price,
      date_price_changed=None,
      date_removed=None,
      price=raw_item.price)

  def __init__(self, db_name):
    self.db_name = db_name
    self.connection = None

  def connect(self):
    self.connection = sqlite3.connect(self.db_name)

  def create_table(self):
    self.connection.execute('''
    CREATE TABLE IF NOT EXISTS prices
      (
        postcode_district     TEXT,
        postcode              TEXT,
        lat                   INTEGER NOT NULL,
        lng                   INTEGER NOT NULL,
        bedrooms              INTEGER NOT NULL,
        type                  INTEGER NOT NULL,
        date_added            INTEGER NOT NULL,
        price_added           INTEGER NOT NULL,
        date_price_changed    INTEGER,
        date_removed          INTEGER,
        price         INTEGER NOT NULL,
        PRIMARY KEY (lat, lng, bedrooms, type, date_removed)
      )
        ''')

  def update(self, date, postcode_district, postcodes, prices):
    """prices: prices for the specified postcode district and and date (Prices.Data)
    """
    self.create_table()

    raw_items_db = [PricesDb.row_from_prices_raw_item(r) for r in prices.raw_items if r.bedrooms is not None]
    raw_items_db_df = pandas.DataFrame(raw_items_db)
    # Group by key and aggregate the price
    raw_items_db_df_grouped = raw_items_db_df.groupby(['lat', 'lng', 'bedrooms', 'ptype'])
    raw_items_db_df_grouped_agg = raw_items_db_df_grouped.agg({'price' : 'mean'})

    print(f"Update for date {date.isoformat()}. Processing {len(raw_items_db_df_grouped_agg)} data points")

    cur = self.connection.cursor()
    cur.execute('SELECT * from prices WHERE postcode_district=:p', {'p' : postcode_district})
    current_db_rows = cur.fetchall()

    n_price_changed, n_removed, updates = 0, 0, []
    for r in current_db_rows:
      r_db = PricesDb.row_from_db_row(r)
      if r_db.date_removed is not None:
        # This record belongs to the history and can be skipped
        continue
      label = (r_db.lat, r_db.lng, r_db.bedrooms, r_db.ptype)
      try:
        r_agg = raw_items_db_df_grouped_agg.loc[label]
      except:
        # r_db not found, that means it has been removed
        r_db = r_db._replace(date_removed=db_utils.date2int(date))
        n_removed += 1
        updates.append(r_db)
        continue
      raw_items_db_df_grouped_agg = raw_items_db_df_grouped_agg.drop(label)
      new_price = r_agg['price']
      if r_db.price != new_price:
        r_db = r_db._replace(date_price_changed=db_utils.date2int(date), price=new_price)
        n_price_changed += 1
        updates.append(r_db)

    # now only new records are left in raw_items_db_df_grouped_agg
    print(f"price changed: {n_price_changed}, removed from market: {n_removed}, new: {len(raw_items_db_df_grouped_agg)}")

    for i in raw_items_db_df_grouped_agg.index:
      v = raw_items_db_df_grouped_agg.loc[i]
      p=v['price']
      r = PricesDb.Row(
        postcode_district=postcode_district,
        postcode=postcodes.find(db_utils.int2latlng(i[0], i[1])),
        lat=i[0],
        lng=i[1],
        bedrooms=i[2],
        ptype=i[3],
        date_added=db_utils.date2int(date),
        price_added=p,
        date_price_changed=None,
        date_removed=None,
        price=p
      )
      self.connection.execute(
        """INSERT INTO prices VALUES (
        :postcode_district,
        :postcode,
        :lat,
        :lng,
        :bedrooms,
        :ptype,
        :date_added,
        :price_added,
        :date_price_changed,
        :date_removed,
        :price
        )      
        """, r._asdict())

    # update existing rows
    for r in updates:
      cur = self.connection.execute(
        """UPDATE prices SET
            date_removed = :date_removed,
            date_price_changed = :date_price_changed,
            price = :price
        WHERE
          lat=:lat AND
          lng=:lng AND
          bedrooms=:bedrooms AND
          type=:ptype AND
          date_removed IS NULL
        """, r._asdict())
      assert(cur.rowcount == 1)

  
def fill_database(postcode, dates):
  prices_db = PricesDb('test_db/propertydata.db')
  postcodes = Postcodes()
  with open(os.path.join('postcodes', f'{postcode}.csv')) as f:
    postcodes.load_csv(f)

  for d in dates:
    prices_db.connect()
    with open(os.path.join('test_datasets', 'prices', postcode, f'{d.isoformat()}.json')) as f:
      p = Prices.load(f)
    prices_db.update(d, postcode, postcodes, p)
    prices_db.connection.commit()
    prices_db.connection.close()

def update_today(postcode):
  dates = [datetime.date.today()]
  fill_database(postcode, dates)

def update_all(postcode):

  dates = os.listdir(os.path.join('test_datasets', 'prices', postcode))
  dates = [datetime.date.fromisoformat(d.split('.')[0]) for d in dates]
  dates.sort()
  fill_database(postcode, dates)

if __name__ == '__main__':
  postcode = 'RG14'
  update_today(postcode)
  #update_all(postcode)



