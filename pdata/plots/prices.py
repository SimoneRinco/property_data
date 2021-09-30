from pdata.req.prices import Data
from pdata.enums import PROPERTY_TYPES, PropertyType, property_type2prettystr
from pdata.plots.colors import get_color

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from collections import defaultdict
import json
import os


def prices_plots(data):

  def def_factory():
    return defaultdict(list)

  grouped_data = defaultdict(def_factory)

  for r in data.raw_items:
    grouped_data[r.ptype][r.bedrooms if r.bedrooms is not None else 0].append(r.price)

  fig = plt.figure()
  fig.suptitle(f'Prices ({data.points_analysed} properties) in {data.postcode}')

  beds = range(2, 6)
  gs = GridSpec(nrows=len(PROPERTY_TYPES), ncols=len(beds))
  for index, ptype in enumerate(PROPERTY_TYPES):
    for bed_index, nbeds in enumerate(beds):
      ax = fig.add_subplot(gs[index, bed_index])
      ax.set_title(f'{property_type2prettystr(ptype)}, {nbeds} beds')
      color = get_color(ptype, nbeds)
      if color is not None:
        prices = grouped_data[ptype][nbeds]
        if len(prices) > 0:
          ax.hist(prices, bins=20, color=color, label=f'{nbeds} bed [{len(prices)}]')
      ax.legend()

  plt.show()


if __name__ == '__main__':
  with open(os.path.join('test_datasets', 'prices.json')) as f:
    j = json.load(f)

  data = Data(j)
  prices_plots(data)