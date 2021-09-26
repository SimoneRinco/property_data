from pdata.enums import PropertyType, str2property_type, property_type2str
from pdata.coordinates import LatLng, dict2coo
from pdata.postcode import sanitize as postcode_sanitize
from pdata.req import get_json
from pdata.pdkey import PKEY

import datetime
import json
import os


class Data(object):

  class RawItem(object):

    def __init__(self, d):
      """Initialisation from the dictionary returned by the sold-prices Property Data API call
      """
      # fill the None fields if required
      self.date = datetime.date.fromisoformat(d['date'])
      self.address = None
      self.price = int(d['price'])
      self.coordinates = dict2coo(d)
      b = d['bedrooms']
      if b is not None:
        b = int(b)
      self.bedrooms = b
      self.ptype = str2property_type(d['type'])
      self.tenure = None
      self.pclass = None
      self.distance = None

  def __init__(self, d):
    self.raw_items = []
    for r in d['data']['raw_data']:
      self.raw_items.append(Data.RawItem(r))
    self.date_earliest = datetime.date.fromisoformat(d['data']['date_earliest'])
    self.date_latest = datetime.date.fromisoformat(d['data']['date_latest'])
    

def req_sold_prices(postcode, max_age=12, ptype=None, npoints=100):

  postcode = postcode_sanitize(postcode)
  params = {
    'key' : PKEY,
    'postcode' : postcode_sanitize(postcode),
    'max_age' : str(max_age),
    'points' : str(npoints)
    }

  if ptype is not None:
    params['type'] = property_type2str(ptype)

  url ='https://api.propertydata.co.uk/sold-prices'
  return get_json(url, **params)
  

if __name__ == '__main__':

  j = req_sold_prices("RG14 2FB")
  with open('tmp', 'w') as f:
    json.dump(j, f)
  d = Data(j)
  for r in d.raw_items:
    print(r.price)

