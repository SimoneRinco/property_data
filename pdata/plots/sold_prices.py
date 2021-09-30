from pdata.plots.colors import get_color
from pdata.req.sold_prices import Data
from pdata.enums import PROPERTY_TYPES, property_type2prettystr

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from collections import defaultdict
import os
import json
import datetime

def sold_prices_plots(data, min_date=None):

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
    else:
      pass

  fig = plt.figure()
  fig.suptitle(f'Sold prices ({data.points_analysed} properties) in {data.postcode} (radius={data.radius}) from {min_date} to {data.date_latest}')

  gs = GridSpec(nrows=len(PROPERTY_TYPES), ncols=1)
  for index, ptype in enumerate(PROPERTY_TYPES):
    ax = fig.add_subplot(gs[index, 0])
    ax.set_title(property_type2prettystr(ptype))
    for nbeds in range(2, 5):
      color = get_color(ptype, nbeds)
      if color is not None:
        prices = grouped_data[ptype][nbeds]
        if len(prices) > 0:
          ax.hist(prices, bins=40, range=(180000, 650000), alpha=0.5, color=color, label=f'{nbeds} bed [{len(prices)}]')
    ax.legend()

  plt.show()


if __name__ == '__main__':
  with open(os.path.join('test_datasets', 'sold_prices.json')) as f:
    j = json.load(f)

  data = Data(j)
  min_date = datetime.date(2021, 3, 1)
  #min_date = None
  sold_prices_plots(data, min_date=min_date)
