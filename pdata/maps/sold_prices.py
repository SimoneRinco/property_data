from pdata.maps.mapgen import *
from pdata.enums import PropertyType, property_type2prettystr
from pdata.sold_prices import Data as SoldPricesData

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import datetime
from collections import defaultdict
import json

def gen_sold_prices_map(data, min_date=None):
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


def gen_sold_prices_charts(data, min_date=None):

  colors = {
    PropertyType.SEMI_DETACHED : [None, None, None, 'skyblue', 'steelblue', 'dodgerblue'],
    PropertyType.DETACHED : [None, None, None, 'lawngreen', 'lightgreen', 'lime', 'forestgreen', 'darkgreen'],
    }

  def def_factory():
    return defaultdict(list)

  grouped_data = defaultdict(def_factory)

  if min_date is None:
    min_date = data.date_earliest
  else:
    if data.date_earliest > min_date:
      raise RuntimeError(f'min date ({min_date}) is before earliest date ({data.date_earliest})')

  for r in data.raw_items:
    if min_date is None or r.date >= min_date:
      grouped_data[r.ptype][r.bedrooms if r.bedrooms is not None else 0].append(r.price)

  fig = plt.figure()
  fig.suptitle(f'Sold prices from {min_date} to {data.date_latest}')

  gs = GridSpec(nrows=len(colors.keys()), ncols=1)
  for index, (ptype, colors_per_bedroom) in enumerate(colors.items()):
    ax = fig.add_subplot(gs[index, 0])
    ax.set_title(property_type2prettystr(ptype))
    for bedrooms, color in enumerate(colors_per_bedroom, start=0):
      if color is not None:
        prices = grouped_data[ptype][bedrooms]
        if len(prices) > 0:
          ax.hist(prices, bins=40, range=(250000, 650000), alpha=0.5, color=color, label=f'{bedrooms} bed [{len(prices)}]')
    ax.legend()

  plt.show()


if __name__ == '__main__':

  with open('sold_prices.json') as f:
    j = json.load(f)

  data = SoldPricesData(j)
  #min_date = datetime.date(2021, 3, 1)
  min_date = None
  #gen_sold_prices_map(data, min_date=min_date)
  gen_sold_prices_charts(data, min_date=min_date)


