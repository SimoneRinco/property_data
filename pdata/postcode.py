from pdata import req
from pdata.coordinates import LatLng, distance

import csv

def sanitize_postcode(postcode):
  return ' '.join(postcode.split()).upper()


def to_lat_lng(postcode):

  # We can use a postcode BD instead (or just a csv file)
  key='17o8dysaCDrgv1c'

  p = sanitize_postcode(postcode)
  j = req.get_json('https://api.promaptools.com/service/uk/postcode-lat-lng/get/', postcode=p, key=key)
  out0 = j['output'][0]
  return out0['latitude'], out0['longitude']


class Postcodes(object):

  def __init__(self):
    self.postcodes = {}

  def load_csv(self, fileobj):
    reader = csv.DictReader(fileobj)
    for line in reader:
      if line['In Use?'] == "Yes":
        self.postcodes[sanitize_postcode(line['Postcode'])] = \
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

    return ret

if __name__ == '__main__':
  print(to_lat_lng("rg14  1nu"))
