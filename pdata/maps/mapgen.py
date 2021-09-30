from pdata.coordinates import LatLng
from pdata.maps.mkey import MKEY
from pdata.enums import PropertyType
from pdata.req.req import get as req_get

from collections import namedtuple
from enum import Enum
from enum import auto as eauto

class MarkerSize(Enum):
  DEFAULT = eauto()
  TINY = eauto()
  MID = eauto()
  SMALL = eauto()

class MarkerColor(Enum):
  BLACK = eauto()
  BROWN = eauto()
  GREEN = eauto()
  PURPLE = eauto()
  YELLOW = eauto()
  BLUE = eauto()
  GRAY = eauto()
  ORANGE = eauto()
  RED = eauto()
  WHITE = eauto()

MapSize = namedtuple('MapSize', 'x y')

class Marker:
  
  def __init__(self, size=MarkerSize.DEFAULT, color=MarkerColor.RED, label=None, locations=None):
    self.size = size
    self.color = color
    if label is not None:
      if self.size != MarkerSize.DEFAULT and self.size != MarkerSize.MID:
        raise RuntimeError(f'Cannot set label for marker size {str(self.size)}')
      # sanity check
      if len(label) != 1:
        raise RuntimeError(f'Marker labels must have size 1 (single character)')
      if not label.isalnum():
        raise RuntimeError(f'Marker labels must have alphanumeric')
      self.label = label
    self.locations = locations

  def add_location(l):
    self.locations.append(l)

  def encode(self):
    if self.locations is None or len(self.locations) == 0:
      raise RuntimeError(f'Failed to encode marker: there are no locations')

    style = []
    # size
    if self.size != MarkerSize.DEFAULT:
      style.append(f'size:{str(self.size.name).lower()}')
    # color
    style.append(f'color:{str(self.color.name).lower()}')
    # label
    if self.label is not None:
      style.append(f'label:{str(self.label)}')

    style_str = '|'.join(style)
    coo_str = '|'.join([f'{str(c.lat)},{str(c.lng)}' for c in self.locations])

    return '|'.join([style_str, coo_str])


def gen_static(map_size, out_file, **params):
  url ='https://maps.googleapis.com/maps/api/staticmap'
  if 'key' in params:
    raise RuntimeError('Parameters must not have a "key" key')
  if 'size' in params:
    raise RuntimeError('Parameters must not have a "size" key. Provide the size via the map_size argument')

  params['key'] = MKEY
  params['size'] = 'x'.join([str(map_size.x), str(map_size.y)])

  r = req_get(url, **params)
  for chunk in r.iter_content(chunk_size=128):
    out_file.write(chunk)


def ptype2mcolor(ptype):
  if ptype == PropertyType.FLAT:
    return MarkerColor.BROWN
  if ptype == PropertyType.TERRACED:
    return MarkerColor.ORANGE
  if ptype == PropertyType.SEMI_DETACHED:
    return MarkerColor.BLUE
  if ptype == PropertyType.DETACHED:
    return MarkerColor.GREEN
  raise RuntimeError("unknown property type")


def gen_static_from_markers(map_size, out_file, markers):
  params = {'markers' : []}
  for m in markers:
    params['markers'].append(m.encode())
  gen_static(map_size, out_file, **params)

if __name__ == '__main__':
  m1 = Marker(label='A', locations=[LatLng(lat=51.40513200, lng=-1.29996670)])
  m2 = Marker(label='V', color=MarkerColor.YELLOW, locations=[
    LatLng(lat=51.40498780, lng=-1.30035410),
    LatLng(lat=51.40603090, lng=-1.29990990)
    ])

  with open('static_from_markers.png', 'wb') as f:
    gen_static_from_markers(MapSize(x=800, y=800), f, [m1, m2])

