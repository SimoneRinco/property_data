from pdata.req.prices import Prices
from pdata.enums import PropertyType, property_type2short
import datetime

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from collections import defaultdict
import os
import math

if __name__ == '__main__':

  ptypes = [PropertyType.SEMI_DETACHED, PropertyType.DETACHED]
  beds = [3, 4, 5]

  dirname = 'test_datasets/prices/RG14'
  dir = os.listdir(dirname)
  all_dates = []
  all_prices = []

  for prices_file in dir:
    all_dates.append(datetime.date.fromisoformat(prices_file[:10]))
    prices = defaultdict(list)
    with open(os.path.join(dirname, prices_file)) as f:
      prices_data = Prices.load(f)
      for p in prices_data.raw_items:
        for pt in ptypes:
          for b in beds:
            if p.ptype == pt and p.bedrooms == b:
              prices[(pt, b)].append(p.price)
    prices = {k : (len(v), sum(v) / len(v)) for k, v in prices.items()}
    all_prices.append(prices)

  fig = plt.figure()
  gs = GridSpec(nrows=len(ptypes), ncols=len(beds) * 2)
  for ip, p in enumerate(ptypes):
    for ib, b in enumerate(beds):
      col = ib*2
      ax0 = fig.add_subplot(gs[ip, col])
      y = [price[(p, b)][1] for price in all_prices]
      ax0.plot(all_dates, y, '.-')
      ax0.set_title(f"{property_type2short(p)}, {b} beds (prices)")
      ax0.xaxis.set_major_locator(mdates.DayLocator())
      ax1 = fig.add_subplot(gs[ip, col + 1])
      y = [price[(p, b)][0] for price in all_prices]
      ax1.plot(all_dates, y, 'r.-')
      ax1.set_title(f"{property_type2short(p)}, {b} beds (#properties)")
      ax1.xaxis.set_major_locator(mdates.DayLocator())

  plt.show()
    




