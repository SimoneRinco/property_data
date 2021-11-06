from pdata.req.prices import Prices
from pdata.enums import PropertyType, property_type2short
import datetime

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from collections import defaultdict
import os
import math
import statistics

if __name__ == '__main__':

  postcode = "OX3"

  ptypes = [PropertyType.SEMI_DETACHED] #, PropertyType.DETACHED]
  beds = [3] #, 4]

  dirname = os.path.join('test_datasets', 'prices', postcode)
  dir = os.listdir(dirname)
  all_dates = []
  all_prices = []
  all_prices_mean = []
  all_prices_median = []

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
    prices_mean = {k : statistics.mean(v) for k, v in prices.items()}
    prices_median = {k : statistics.median(v) for k, v in prices.items()}

    all_prices.append(prices)
    all_prices_mean.append(prices_mean)
    all_prices_median.append(prices_median)

  fig = plt.figure()
  fig.suptitle(f"prices trend in {postcode}")
  gs = GridSpec(nrows=2 * len(ptypes) + 1, ncols=len(beds))
  for ip, p in enumerate(ptypes):
    for ib, b in enumerate(beds):
      ax0 = fig.add_subplot(gs[2*ip, ib])     
      y = [prices[(p, b)] for prices in all_prices]
      ax0.boxplot(y, positions=mdates.date2num(all_dates))
      ax0.set_title(f"{property_type2short(p)}, {b} beds (prices)")
      ax0.xaxis.set_major_locator(mdates.MonthLocator())
      ax0.xaxis.set_minor_locator(mdates.WeekdayLocator())
      ax0.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))

      ax0 = fig.add_subplot(gs[2*ip + 1, ib])     
      ax0.plot(all_dates, [prices[(p, b)] for prices in all_prices_mean])
      ax0.plot(all_dates, [prices[(p, b)] for prices in all_prices_median])
      ax0.set_title(f"{property_type2short(p)}, {b} beds (prices)")
      ax0.xaxis.set_major_locator(mdates.MonthLocator())
      ax0.xaxis.set_minor_locator(mdates.WeekdayLocator())
      ax0.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))


  ax1 = fig.add_subplot(gs[2*len(ptypes), :])
  ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
  ax1.xaxis.set_minor_locator(mdates.WeekdayLocator())
  ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
  legend = []
  for p in ptypes:
    for b in beds:
      n = [len(prices[(p, b)]) for prices in all_prices]
      ax1.plot(all_dates, n)
      legend.append(f"{property_type2short(p)}, {b} beds")
  ax1.legend(legend)

  plt.show()    
