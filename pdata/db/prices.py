from pdata.req.prices import Prices
import pdata.db.utils as db_utils

import sqlite3


class PricesDb(object):

  class Row(object):

    def __init__(self):
      self.postcode_district = None
      self.latlng = None
      self.bedrooms = None
      self.ptype = None
      self.trans_id = None
      self.date_added = None
      self.price_added = None
      self.date_price_reduced = None
      self.date_price_reduced = None
      self.date_sold = None
      self.date_sold = None
      self.price_sold = None
      self.price = None


    def load_from_db_row(self, tuple):
      self.postcode_district = tuple[0]
      self.latlng = db_utils.int2latlng(tuple[1], tuple[2])
      self.bedrooms = tuple[3]
      self.ptype = db_utils.int2ptype(tuple[4])
      self.trans_id = tuple[5]
      self.date_added = db_utils.int2date(tuple[6])
      self.price_added = tuple[7]
      self.date_price_reduced = db_utils.int2date(tuple[8])
      self.date_sold = db_utils.int2date(tuple[9])
      self.price_sold = tuple[10]
      self.price = tuple[11]

    def load_from_raw_item(self, date, postcode, raw_item):
      self.postcode_district = postcode
      self.latlng = raw_item.coordinates
      self.bedrooms = raw_item.bedrooms
      self.ptype = raw_item.ptype
      self.trans_id = 0
      self.date_added = date 
      self.price_added = raw_item.price
      self.date_price_reduced = None
      self.date_sold = None
      self.price = raw_item.price

    def to_db_row(self):
      return (
        self.postcode_district,
        db_utils.latlng2int(self.latlng)[0],
        db_utils.latlng2int(self.latlng)[1],
        self.bedrooms,
        db_utils.ptype2int(self.ptype),
        self.trans_id,
        db_utils.date2int(self.date_added),
        self.price_added,
        db_utils.date2int(self.date_price_reduced),
        db_utils.date2int(self.date_sold),
        self.price
      )


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
        transaction_id        INTEGER NOT NULL,
        date_added            INTEGER NOT NULL,
        price_added           INTEGER NOT NULL,
        date_price_reduced    INTEGER,
        date_sold             INTEGER,
        price                 INTEGER NOT NULL,
        PRIMARY KEY (lat, lng, bedrooms, type)
      )
        ''')

  def update(date, postcode_district, new_prices):
    """prices: Prices.Data
    """
    cur = self.connection.cursor()
    cur.execute('SELECT * from prices WHERE postcode_district=:postcode', {'postcode' : postcode_district})
    rows = cur.fetchall()

    for item in prices.raw_items:
      

if __name__ == '__main__':

  prices_db = PricesDb('test_db/propertydata.db')
  prices_db.connect()



  # Insert a row of data
  prices_db.connection.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

  # Save (commit) the changes
  prices_db.connection.commit()

  # We can also close the connection if we are done with it.
  # Just be sure any changes have been committed or they will be lost.
  prices_db.connection.close()


