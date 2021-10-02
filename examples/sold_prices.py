from pdata.req.sold_prices import SoldPrices
from pdata.enums import PropertyType, property_type2prettystr

import matplotlib.pyplot as plt
from sklearn import linear_model

import json

from datetime import date
import os

if __name__ == "__main__":

  postcode = "RG14"
  dir = os.path.join('sold_prices', postcode)
  d = date.today()
  filepath = os.path.join(dir, f'{d.isoformat()}.json')

  if not os.path.exists(dir):
    os.makedirs(dir)

  if not os.path.exists(filepath):
    j = SoldPrices.req(postcode=postcode, max_age=60)
    with open(filepath, 'w') as f:
      json.dump(j, f)
    sold_prices = SoldPrices.Data(j)
  else:
    with open(filepath) as f:
      sold_prices = SoldPrices.load(f)

  dates, prices = [], []

  ptypes = [PropertyType.SEMI_DETACHED]
  beds = [3, 4]

  min_date = date.fromisoformat('2020-03-01')
  max_price = 550000

  for r in sold_prices.raw_items:
    if r.ptype in ptypes and r.bedrooms in beds and r.date >= min_date and r.price <= max_price:
      dates.append(r.date)
      prices.append(r.price)

  reg = linear_model.LinearRegression()
  d0 = dates[0]
  reg.fit([[(d - d0).days] for d in dates], prices)
  #print(reg.coef_)
  #print(reg.intercept_)

  min_date = min(dates)
  max_date = max(dates)

  p1 = reg.intercept_ + (min_date - d0).days * reg.coef_
  p2 = reg.intercept_ + (max_date - d0).days * reg.coef_

  fig = plt.figure()
  ax = fig.subplots()

  fig .suptitle(f'Prices for {[property_type2prettystr(p) for p in ptypes]}, {beds} bedrooms')
  ax.scatter(dates, prices, label='Price')
  ax.plot([min_date, max_date], [p1, p2], 'r-', label=f"Daily increase: {reg.coef_[0]}")
  ax.legend()
  plt.show()

  
