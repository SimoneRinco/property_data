from pdata.req.prices import Prices
from pdata.enums import PropertyType, property_type2short
from pdata.plots.colors import get_color
import datetime

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

import numpy as np

from collections import defaultdict
import os
import math
import statistics

class PricesTrend(object):

  def __init__(self, postcode):
    dirname = os.path.join('test_datasets', 'prices', postcode)
    dir = os.listdir(dirname)
    self.__dates = []
    self.__prices = []
    self.__prices_mean = []
    self.__prices_median = []

    for prices_file in dir:
      self.__dates.append(datetime.date.fromisoformat(prices_file[:10]))
      date_prices = defaultdict(list)
      with open(os.path.join(dirname, prices_file)) as f:
        prices_data = Prices.load(f)
      for p in prices_data.raw_items:
        if p.ptype is not None and p.bedrooms is not None:
          date_prices[(p.ptype, p.bedrooms)].append(p.price)
      date_prices_mean = {k : statistics.mean(v) for k, v in date_prices.items()}
      date_prices_median = {k : statistics.median(v) for k, v in date_prices.items()}

      self.__prices.append(date_prices)
      self.__prices_mean.append(date_prices_mean)
      self.__prices_median.append(date_prices_median)

  @property
  def dates(self):
    return self.__dates

  def prices(self, ptype, nbeds):
    return [p[(ptype, nbeds)] for p in self.__prices]

  def overall_prices(self, ptypes, beds):
    ret = []
    for prices in self.__prices:
      all_prices = []
      for p in ptypes:
        for b in beds:
          all_prices.extend(prices[(p, b)])
      ret.append(all_prices)
    return ret

  def prices_mean(self, ptype, nbeds):
    return [mean[(ptype, nbeds)] for mean in self.__prices_mean]

  def prices_median(self, ptype, nbeds):
    return [median[(ptype, nbeds)] for median in self.__prices_median]

  def overall_mean(self, ptypes, beds):
    return [statistics.mean(ov) for ov in self.overall_prices(ptypes, beds)]

  def overall_median(self, ptypes, beds):
    return [statistics.median(ov) for ov in self.overall_prices(ptypes, beds)]

  def n_properties(self, ptype, nbeds):
    return [len(p[(ptype, nbeds)]) for p in self.__prices]


#def draw_boxplot(ax, dates, prices):
#  ax.boxplot(prices, positions=mdates.date2num(dates))
#  set_dates_xaxis(ax)

def set_dates_xaxis(ax):
  ax.xaxis.set_major_locator(mdates.MonthLocator())
  ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))

def set_y_grid(ax, min_y, max_y, minor_step=20000, major_step=100000):

  max_minor_tick = math.ceil(max_y/minor_step)*minor_step
  min_minor_tick = math.floor(min_y/minor_step)*minor_step

  max_major_tick = math.ceil(max_y/major_step)*major_step
  min_major_tick = math.floor(min_y/major_step)*major_step

  major_ticks = np.arange(
    math.ceil(min_minor_tick/major_step)*major_step,
    math.floor(max_minor_tick/major_step)*major_step + 1,
    major_step)
  ax.set_yticks(major_ticks)
  ax.grid(axis='y', which='major', linestyle='--', linewidth=2)

  minor_ticks = np.arange(min_minor_tick, max_major_tick, minor_step)
  ax.set_yticks(minor_ticks, minor=True)  
  ax.grid(axis='y', which='minor', linestyle='--', linewidth=1)


def update_minmax(current_min, current_max, data):
  return min(current_min, min(data)), max(current_max, max(data))

def main():

  postcode = "RG14"

  ptypes = [PropertyType.SEMI_DETACHED, PropertyType.DETACHED]
  beds = [3, 4]

  data = PricesTrend(postcode)

  dates = data.dates

  fig = plt.figure()
  fig.suptitle(f"prices trend in {postcode}")
  gs = GridSpec(nrows=2, ncols=2)

  # mean
  ax = fig.add_subplot(gs[0, 0])
  ax.set_title(f"Mean prices")
  set_dates_xaxis(ax)

  min_price, max_price = math.inf, -math.inf
  for p in ptypes:
    for b in beds:
      y = data.prices_mean(p, b)
      min_price, max_price = update_minmax(min_price, max_price, y)
      ax.plot(dates, y, color=get_color(p, b), label=f"{property_type2short(p)}, {b} beds")

  set_y_grid(ax, min_price, max_price)
  ax.legend(loc="upper right")

  # median
  ax = fig.add_subplot(gs[0, 1])
  ax.set_title(f"Median prices")
  set_dates_xaxis(ax)

  min_price, max_price = math.inf, -math.inf
  for p in ptypes:
    for b in beds:
      y = data.prices_mean(p, b)
      min_price, max_price = update_minmax(min_price, max_price, y)
      ax.plot(dates, y, color=get_color(p, b))

  set_y_grid(ax, min_price, max_price)

  # number of properties
  ax = fig.add_subplot(gs[1, 0])
  ax.set_title(f"Number of properties available")
  set_dates_xaxis(ax)
  min_n, max_n = math.inf, -math.inf
  for p in ptypes:
    for b in beds:
      y = data.n_properties(p, b)
      min_n, max_n = update_minmax(min_n, max_n, y)
      ax.plot(dates, y, color=get_color(p, b))
  set_y_grid(ax, min_n, max_n, minor_step = 10, major_step=20)

  # overall mean and median
  ax = fig.add_subplot(gs[1, 1])
  ax.set_title(f"Overall prices")
  set_dates_xaxis(ax)
  min_n, max_n = math.inf, -math.inf
  y1 = data.overall_mean(ptypes, beds)
  y2 = data.overall_median(ptypes, beds)
  min_n, max_n = update_minmax(min_n, max_n, y1)
  min_n, max_n = update_minmax(min_n, max_n, y2)
  ax.plot(dates, y1, color='red', label='mean')
  ax.plot(dates, y2, color='blue', label='median')
  ax.legend()
  set_y_grid(ax, min_n, max_n, minor_step=2000, major_step=10000)

  plt.show()    


if __name__ == '__main__':
  main()