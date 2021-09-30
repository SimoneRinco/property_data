from pdata.postcode import sanitize as postcode_sanitize

from collections import namedtuple
import math

LatLng = namedtuple('LatLng', ['lat', 'lng'])

def dict2coo(d):
  """It looks for 'lat' and 'lng' keywords in the dict
  """
  return LatLng(lat=float(d['lat']), lng=float(d['lng']))


def distance(p1, p2):

  rad_const = math.pi / 180

  delta_lat = (p1.lat - p2.lat) * rad_const
  delta_lng = (p1.lng - p2.lng) * rad_const

  slat = math.sin(delta_lat/2)
  slng = math.sin(delta_lng/2)

  a = slat*slat + math.cos(p1.lat * rad_const) * math.cos(p2.lat * rad_const) * slng*slng
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  return 6371e3 * c


class PostcodeFinder(object):

  def __init__(self):
    self.postcodes = {}

  def load_csv(self, reader):
    for line in reader:
      if line['In Use?'] == "Yes":
        self.postcodes[postcode_sanitize(line['Postcode'])] = \
          LatLng(
            lat=float(line['Latitude']),
            lng=float(line['Longitude'])
            )

  def find(self, lat_lng):
    ret = ''
    min_dist = 1e100

    for postcode, postcode_center in self.postcodes.items():
      d = distance(lat_lng, postcode_center)
      if d < min_dist:
        min_dist = d
        ret = postcode

    return ret, min_dist


if __name__ == "__main__":

  import csv

  postcode_finder = PostcodeFinder()
  with open("postcodes/RG14.csv") as f:
    r = csv.DictReader(f)
    postcode_finder.load_csv(r)


  print(postcode_finder.find(LatLng(51.40647170213218, -1.3269289786844287)))




