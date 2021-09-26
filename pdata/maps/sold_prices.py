from pdata.maps.mapgen import *
from pdata.enums import PropertyType
from pdata.sold_prices import Data as SoldPricesData

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from collections import defaultdict
import json

def gen_sold_prices_map(data):
  """
  data : pdata.sold_prices.Data
  """

  def def_factory():
    return defaultdict(list)

  markers_data = defaultdict(def_factory)

  for r in data.raw_items:
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


def gen_sold_prices_charts(data):

  def def_factory():
    return defaultdict(list)

  grouped_data = defaultdict(def_factory)

  for r in data.raw_items:
    grouped_data[r.ptype][r.bedrooms if r.bedrooms is not None else 0].append(r.price)

  fig = plt.figure()
  gs = GridSpec(nrows=2, ncols=1)
  ax0 = fig.add_subplot(gs[0, 0])
  ax0.hist(grouped_data[PropertyType.SEMI_DETACHED][3], alpha=0.5)
  ax0.hist(grouped_data[PropertyType.SEMI_DETACHED][4], alpha=0.5)
  ax1 = fig.add_subplot(gs[1, 0])
  ax1.hist(grouped_data[PropertyType.DETACHED][3], alpha=0.5)
  ax1.hist(grouped_data[PropertyType.DETACHED][4], alpha=0.5)

  plt.show()


if __name__ == '__main__':

  with open('tmp.json') as f:
    j = json.load(f)

  data = SoldPricesData(j)
  #gen_sold_prices_map(data)
  gen_sold_prices_charts(data)


