from pdata.maps.mapgen import *
from pdata.enums import PropertyType, property_type2prettystr
from pdata.req.prices import Data as PricesData

import datetime
from collections import defaultdict
import json

def prices_map(data, filename, ptypes, price_range=None, bed_range=None):
  """
  data : pdata.prices.Data
  """

  def def_factory():
    return defaultdict(list)

  markers_data = defaultdict(def_factory)

  min_price = -1 if price_range is None or price_range[0] is None else price_range[0]
  max_price = 1e9 if price_range is None or price_range[1] is None else price_range[1]

  min_beds = -1 if bed_range is None or bed_range[0] is None else bed_range[0]
  max_beds = 100 if bed_range is None or bed_range[1] is None else bed_range[1]

  for r in data.raw_items:
    if r.ptype in ptypes:      
      if r.bedrooms is not None and r.bedrooms >= min_beds and r.bedrooms <= min_beds:
        if r.price >= min_price and r.price <= max_price:
          markers_data[r.ptype][r.bedrooms].append(r.coordinates)

  markers = []
  for prop_key, prop_data in markers_data.items():
    for bed_key, bed_data in prop_data.items():
      markers.append(Marker(label=str(bed_key), color=ptype2mcolor(prop_key), locations=bed_data))

  size = MapSize(1200, 1200)
  with open(filename, 'wb') as f:
    gen_static_from_markers(size, f, markers)


if __name__ == '__main__':

  with open('test_datasets/prices_RG14.json') as f:
    j = json.load(f)

  data = PricesData(j)
  prices_map(data, 'prices_tmp.png',
             [PropertyType.SEMI_DETACHED, PropertyType.DETACHED],
             [None, 500000],
             [3, 4]
             )