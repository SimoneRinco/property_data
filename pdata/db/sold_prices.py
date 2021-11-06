from pdata.req.sold_prices import SoldPrices
import pdata.db.utils as db_utils

import sqlite3
from datetime import date
from collections import namedtuple
import os


class SoldPricesDb(object):

  Row = namedtuple('Row',
                   ['postcode_district',
                    'postcode',
                    'address',
                    'lat',
                    'lng',
                    'bedrooms',
                    'ptype',
                    'date_sold',
                    'price_sold',
                    'date_logged'
                    ])

  def __init__(self, db_name):
    self.db_name = db_name
    self.connection = None

  def connect(self):
    self.connection = sqlite3.connect(self.db_name)


  @staticmethod
  def row_from_sold_prices_raw_item(postcode_district, date_logged, raw_item):
    if raw_item.coordinates is None:
      lat, lng = None, None
    else:
      lat, lng = db_utils.latlng2int(raw_item.coordinates)
    address_split = [a.strip() for a in raw_item.address.split(',')]
    for a in address_split:
      aa = a.split(' ')
      if len(aa) == 2 and aa[0] == postcode_district:
        postcode = a
        break
    else:
      raise RuntimeError(f'Cannot find postcode in address {raw_item.address}')

    return SoldPricesDb.Row(
      postcode_district=postcode_district,
      postcode=postcode,
      address=raw_item.address,
      lat=lat,
      lng=lng, 
      bedrooms=raw_item.bedrooms,
      ptype=db_utils.ptype2int(raw_item.ptype),
      date_sold=db_utils.date2int(raw_item.date),
      price_sold=raw_item.price,
      date_logged=db_utils.date2int(date_logged)
      )


  def create_table(self):
    self.connection.execute('''
    CREATE TABLE IF NOT EXISTS sold_prices
      (
        postcode_district     TEXT,
        postcode              TEXT,
        address               TEXT,
        lat                   INTEGER,
        lng                   INTEGER,
        bedrooms              INTEGER,
        type                  INTEGER NOT NULL,
        date_sold             INTEGER NOT NULL,
        price_sold            INTEGER NOT NULL,
        date_logged           INTEGER NOT NULL,
        PRIMARY KEY (postcode, address, date_sold)
      )
        ''')

  def update(self, postcode_district, date_logged, sold_prices):
    """sold_prices: sold prices for the specified postcode district and and date (SoldPrices.Data)
    """

    self.create_table()
    r_db = [SoldPricesDb.row_from_sold_prices_raw_item(postcode_district, date_logged, r) for r in sold_prices.raw_items]

    new_sold = 0
    for r in r_db:
      cur = self.connection.execute(
        """INSERT OR IGNORE INTO sold_prices VALUES (
        :postcode_district,
        :postcode,
        :address,
        :lat,
        :lng,
        :bedrooms,
        :ptype,
        :date_sold,
        :price_sold,
        :date_logged
        )      
        """, r._asdict())
      new_sold += cur.rowcount

    print (f"{postcode_district}, {date_logged}: {new_sold} new data points")


def fill_database(postcode, dates):

  for d in dates:
    with open(os.path.join('test_datasets', 'sold_prices', postcode, f'{d.isoformat()}.json')) as f:
      p = SoldPrices.load(f)

    db = SoldPricesDb("test_db/propertydata.db")
    db.connect()
    db.update(postcode, d, p)
    db.connection.commit()
    db.connection.close()

def update_today(postcode):
  dates = [datetime.date.today()]
  fill_database(postcode, dates)

def update_all(postcode):

  dates = os.listdir(os.path.join('test_datasets', 'sold_prices', postcode))
  dates = [date.fromisoformat(d.split('.')[0]) for d in dates]
  dates.sort()
  fill_database(postcode, dates)


if __name__ == '__main__':
  postcodes = [
    "OX1", "OX2", "OX3", "OX4", # Oxford
    "OX13", "OX14", # Abingdon
    "RG14", # Newbury
    "RG18", "RG19", # Thatcham
    "RG1", "RG2", "RG4", "RG5", "RG6", # Reading
    "RG9", # Henley on Thames
    ]
  #update_today(postcode)
  for p in postcodes:
    update_all(p)
