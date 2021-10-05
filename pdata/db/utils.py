from pdata.coordinates import LatLng, dict2coo
from pdata.enums import PropertyType

import datetime

DB_DATE_FORMAT = "%Y%m%d"

def date2int(d):
  """d: date
  """
  return int(d.strftime(DB_DATE_FORMAT))


def int2date(d_int):
  return datetime.datetime.strptime(str(d_int), DB_DATE_FORMAT).date()

def latlng2int(ll):
  """l: LatLng
  """
  def float2int(f):
    return int(f*1e6)

  return float2int(ll.lat), float2int(ll.lng)


def int2latlng(lat, lng):
  def int2float(i):
    return float(i)/1e6

  return LatLng(lat=int2float(lat), lng=int2float(lng))


def ptype2int(ptype):
  """ptype: PropertyType
  """
  return ptype.value

def int2ptype(ptype_int):
  # This will fail for invalid integer values
  return PropertyType(ptype_int) 


if __name__ == "__main__":

  l = dict2coo({'lat' : '51.41013000', 'lng': '-1.30775200'})
  lat_int, lng_int = latlng2int(l)
  print(lat_int, lng_int)
  print(int2latlng(lat_int, lng_int))

  d = datetime.date.fromisoformat('2021-09-30')
  d_int = date2int(d)
  print(d_int)
  d2 = int2date(d_int)
  print(d2)

  print(ptype2int(PropertyType.SEMI_DETACHED))
  print(int2ptype(4))

