from pdata.req.prices import Prices
import pdata.db.utils as db_utils

from collections import namedtuple
import datetime
import sqlite3
import os

class PricesDb(object):

  Row = namedtuple('Row',
                   ['postcode_district',
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

  def update(self, date, postcode_district, prices):
    """prices: prices for the specified postcode district and and date (Prices.Data)
    """
    self.create_table()

    cur = self.connection.cursor()
    cur.execute('SELECT * from prices WHERE postcode_district=:p', {'p' : postcode_district})
    rows = cur.fetchall()

    raw_items = [r for r in prices.raw_items if r.bedrooms is not None]

    # prices found in the database (indices)
    prices_found = [False] * len(raw_items)

    updates = []

    for r in rows:
      r_db = PricesDb.row_from_db_row(r)
      if r_db.date_removed is not None:
        # This record belongs to the history and can be skipped
        continue
      for index, raw_item in enumerate(raw_items):
        r_raw = PricesDb.row_from_prices_raw_item(raw_item)
        if (
          r_db.lat == r_raw.lat and
          r_db.lng == r_raw.lng and
          r_db.bedrooms == r_raw.bedrooms and
          r_db.ptype == r_raw.ptype
          ):
          # found an active record
          prices_found[index] = True
          # has the price changed?
          if r_db.price != r_raw.price:
            r_db = r_db._replace(date_price_changed=db_utils.date2int(date), price=r_raw.price)
            updates.append(r_db)
          break
      else:
        # r_db not found, that means it has been removed
        r_db = r_db._replace(date_removed=db_utils.date2int(date))
        updates.append(r_db)

    # now check for new records
    new_records = []
    for found, raw_item in zip(prices_found, raw_items):
      if found:
        continue
      r = PricesDb.row_from_prices_raw_item(raw_item)
      r = r._replace(postcode_district=postcode_district, date_added=db_utils.date2int(date))
      new_records.append(r)
    
    # Insert the new rows
    for r in new_records:
      prices_db.connection.execute(
        """INSERT INTO prices VALUES (
        :postcode_district,
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
      prices_db.connection.execute(
        """UPDATE prices SET (date_removed, date_price_changed, price) = (:date_removed, :date_price_changed, :price)
        WHERE (lat=:lat, lng=:lng, bedrooms=:bedrooms, type=:ptype, date_removed=NULL)
        """, r._asdict())
    

if __name__ == '__main__':

  prices_db = PricesDb('test_db/propertydata.db')
  prices_db.connect()

  postcode='RG14'
  dates=['2021-10-01', '2021-10-02', '2021-10-03', '2021-10-04']
  #dates=['2021-10-01']

  for d in dates:
    with open(os.path.join('test_datasets', 'prices', postcode, f'{d}.json')) as f:
      p = Prices.load(f)
    prices_db.update(datetime.date.fromisoformat(d), postcode, p)

  # Save (commit) the changes
  prices_db.connection.commit()

  # We can also close the connection if we are done with it.
  # Just be sure any changes have been committed or they will be lost.
  prices_db.connection.close()


