from collections import namedtuple

LatLng = namedtuple('LatLng', ['lat', 'lng'])

def dict2coo(d):
  """It looks for 'lat' and 'lng' keywords in the dict
  """
  return LatLng(lat=float(d['lat']), lng=float(d['lng']))