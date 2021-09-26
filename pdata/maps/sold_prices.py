from pdata.maps.mapgen import *
from pdata.enums import PropertyType, property_type2prettystr
from pdata.sold_prices import Data as SoldPricesData

import datetime
from collections import defaultdict
import json

def sold_prices_map(data, min_date=None):
  """
  data : pdata.sold_prices.Data
  """

  def def_factory():
    return defaultdict(list)

  markers_data = defaultdict(def_factory)

  for r in data.raw_items:
    if min_date is None or r.date >= min_date:
      markers_data[r.ptype][r.bedrooms if r.bedrooms is not None else 0].append(r.coordinates)

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

  markers = []
  for prop_key, prop_data in markers_data.items():
    for bed_key, bed_data in prop_data.items():
      markers.append(Marker(label=str(bed_key), color=ptype2mcolor(prop_key), locations=bed_data))

  size = MapSize(1200, 1200)
  with open('sold_prices_tmp.png', 'wb') as f:
    gen_static_from_markers(size, f, markers)


if __name__ == '__main__':

  with open('sold_prices.json') as f:
    j = json.load(f)

  data = SoldPricesData(j)
  #min_date = datetime.date(2021, 3, 1)
  min_date = None
  sold_prices_map(data, min_date=min_date)


