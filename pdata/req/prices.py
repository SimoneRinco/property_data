from pdata.pdkey import PKEY
from pdata.postcode import sanitize_postcode
from pdata.req.req import get_json, MIN_TIME_BETWEEN_API_CALLS
from pdata.coordinates import LatLng, dict2coo
from pdata.enums import PropertyType, str2property_type, property_type2str

import json
import time

class Prices(object):

  class Data(object):

    class RawItem(object):

      def __init__(self, d):
        """Initialisation from the dictionary returned by the prices Property Data API call
        """
        # fill the None fields if required
        self.price = int(d['price'])
        self.coordinates = dict2coo(d)
        b = d['bedrooms']
        if b is not None:
          b = int(b)
        self.bedrooms = b
        self.ptype = str2property_type(d['type'])

    def __init__(self, d):
      self.raw_items = []
      for r in d['data']['raw_data']:
        self.raw_items.append(Prices.Data.RawItem(r))

      self.postcode = d['postcode']
      self.points_analysed = int(d['data']['points_analysed'])

  @staticmethod
  def req(postcode, ptype=None, nbedrooms=None, npoints=100, sleep=True):
    postcode = sanitize_postcode(postcode)
    params = {
      'key' : PKEY,
      'postcode' : sanitize_postcode(postcode),
      'points' : str(npoints)
      }

    if ptype is not None:
      params['type'] = property_type2str(ptype)
    if nbedrooms is not None:
      params['bedrooms'] = str(nbedrooms)

    url ='https://api.propertydata.co.uk/prices'
    ret = get_json(url, **params)
    if sleep:
      time.sleep(MIN_TIME_BETWEEN_API_CALLS)
    return ret
  

  @staticmethod
  def load(fileobj):
    j = json.load(fileobj)
    return Prices.Data(j)

if __name__ == '__main__':

  postcode = "RG14"
  j = req_prices(postcode)
  with open(f'prices_{postcode}', 'w') as f:
    json.dump(j, f)
  d = Data(j)
  for r in d.raw_items:
    print(r.price)