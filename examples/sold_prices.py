from pdata.req.sold_prices import SoldPrices
from pdata.enums import PropertyType, property_type2prettystr

import matplotlib.pyplot as plt
from sklearn import linear_model

import json

from datetime import date, timedelta
import os

if __name__ == "__main__":

  postcodes = [
    "OX1", "OX2", "OX3", "OX4", # Oxford
    "OX13", "OX14", # Abingdon
    "RG14", # Newbury
    "RG18", "RG19", # Thatcham
    "RG1", "RG2", "RG4", "RG5", "RG6", # Reading
    "RG9", # Henley on Thames
    ]

  for postcode in postcodes:
    dir = os.path.join('test_datasets', 'sold_prices', postcode)
    d = date.today()
    filepath = os.path.join(dir, f'{d.isoformat()}.json')

    if not os.path.exists(dir):
      os.makedirs(dir)

    if not os.path.exists(filepath):
      print(f'downloading sold prices for {postcode}')
      j = SoldPrices.req(postcode=postcode, max_age=60)
      with open(filepath, 'w') as f:
        json.dump(j, f)
      sold_prices = SoldPrices.Data(j)
    else:
      with open(filepath) as f:
        print(f'loading sold prices for {postcode}')
        sold_prices = SoldPrices.load(f)

  postcode = "RG14"
  dir = os.path.join('test_datasets', 'sold_prices', postcode)
  d = date.today()
  filepath = os.path.join(dir, f'{d.isoformat()}.json')
  with open(filepath) as f:
    sold_prices = SoldPrices.load(f)

  ptypes = [PropertyType.FLAT, PropertyType.TERRACED, PropertyType.SEMI_DETACHED, PropertyType.DETACHED]
  # Most properties don't have beds info!
  #beds = [3, 4]

  colors = [None, 'blue', 'red', 'gold', 'green', 'fuchsia']

  max_date = d - timedelta(days=120)
  min_date = max_date - timedelta(days=365)
  max_price = 5000000

  fig, ax = plt.subplots(len(ptypes))

  for ip, p in enumerate(ptypes):
    ax[ip].set_title(f'{property_type2prettystr(p)}')
    #for ib, b in enumerate(beds):
    for dummy in range(1):
      dates, prices = [], []
      for r in sold_prices.raw_items:
        #if r.ptype == p and r.bedrooms == b and r.date >= min_date and r.price <= max_price:
        if r.ptype == p and r.date >= min_date and r.date <= max_date and r.price <= max_price:
          dates.append(r.date)
          prices.append(r.price)

      reg = linear_model.LinearRegression()
      d0 = dates[0]
      reg.fit([[(d - d0).days] for d in dates], prices)

      min_date = min(dates)
      max_date = max(dates)

      p1 = reg.intercept_ + (min_date - d0).days * reg.coef_
      p2 = reg.intercept_ + (max_date - d0).days * reg.coef_

      #ax[ip].scatter(dates, prices, label=f'{b} beds', color=colors[b])
      ax[ip].scatter(dates, prices, label=f'all beds', color=colors[1])
      #ax[ip].plot([min_date, max_date], [p1, p2], '-', label=f"Daily incr {b} beds: {reg.coef_[0]:.2f}", color=colors[b])
      ax[ip].plot([min_date, max_date], [p1, p2], '-', label=f"Daily incr all beds: {reg.coef_[0]:.2f}", color=colors[1])
    ax[ip].legend()

  plt.show()

  
