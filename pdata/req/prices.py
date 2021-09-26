from pdata.req import get_json
from pdata.pdkey import PKEY
from pdata.postcode import sanitize as postcode_sanitize
from pdata.coordinates import LatLng, dict2coo
from pdata.enums import PropertyType, str2property_type, property_type2str

import json

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
      self.distance = None

  def __init__(self, d):
    self.raw_items = []
    for r in d['data']['raw_data']:
      self.raw_items.append(Data.RawItem(r))

def req_prices(postcode, bedrooms=None, ptype=None, npoints=None):

  postcode = postcode_sanitize(postcode)
  params = {
    'key' : PKEY,
    'postcode' : postcode_sanitize(postcode),
    }

  if bedrooms is not None:
    params['bedrooms'] = str(bedrooms)

  if ptype is not None:
    params['type'] = property_type2str(ptype)

  if npoints is not None:
    params['points'] = str(npoints)

  url ='https://api.propertydata.co.uk/prices'
  return get_json(url, **params)


if __name__ == '__main__':
  #j = req_prices('RG14 1NU')
  #with open('prices2.json', 'w') as f:
  #  json.dump(j, f)

  with open('prices.json') as f:
    j = json.load(f)
  d = Data(j)
