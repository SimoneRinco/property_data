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

  postcode = "RG14"

  ptypes = [PropertyType.SEMI_DETACHED, PropertyType.DETACHED]
  beds = [3, 4, 5]

  dirname = os.path.join('test_datasets', 'prices', postcode)
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
    all_prices.append(prices)

  fig = plt.figure()
  gs = GridSpec(nrows=len(ptypes) + 1, ncols=len(beds))
  for ip, p in enumerate(ptypes):
    for ib, b in enumerate(beds):
      ax0 = fig.add_subplot(gs[ip, ib])
      y = [prices[(p, b)] for prices in all_prices]
      ax0.boxplot(y, labels=all_dates)
      ax0.set_title(f"{property_type2short(p)}, {b} beds (prices)")

  ax1 = fig.add_subplot(gs[len(ptypes), :])
  ax1.xaxis.set_major_locator(mdates.DayLocator())
  ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
  legend = []
  for p in ptypes:
    for b in beds:
      n = [len(prices[(p, b)]) for prices in all_prices]
      ax1.plot(all_dates, n)
      legend.append(f"{property_type2short(p)}, {b} beds")
  ax1.legend(legend)

  plt.show()    
