from pdata.postcode import Postcodes
from pdata.coordinates import kmeans, find_cluster
from pdata.req.prices import Prices
from pdata.enums import PropertyType, property_type2prettystr
from pdata.maps.mapgen import Marker, MapSize, gen_static_from_markers

import matplotlib.pyplot as plt

from datetime import date
import json
import os

"""Example on how to use the "prices" API, or visualise
prices previously downloaded or retrieved using the API
"""

def gather_today():

  postcodes = [
    "OX1", "OX2", "OX3", "OX4", # Oxford
    "OX13", "OX14", # Abingdon
    "RG14", # Newbury
    "RG18", "RG19", # Thatcham
    "RG1", "RG2", "RG4", "RG5", "RG6", # Reading
    "RG9", # Henley on Thames
    ]

  today = date.today()

  force_download = False

  for postcode in postcodes:
    dir = os.path.join('test_datasets', 'prices', postcode)
    if not os.path.exists(dir):
      os.makedirs(dir)
    prices_filename = os.path.join(dir, f'{today.isoformat()}.json')
    if os.path.exists(prices_filename) and not force_download:
      print(f"Skipping {postcode} as data is already present")
    else:
      print(f"Gathering prices for {postcode}")
      j = Prices.req(postcode=postcode, sleep=True)
      with open(prices_filename, 'w') as f:
        json.dump(j, f)


if __name__ == '__main__':

  # gather all data for today
  gather_today()

  # Display today's data for Newbury, per zone (cluster)

  # load postcodes in Newbury
  postcode = "OX4"
  p = Postcodes()
  with open(f'postcodes/{postcode}.csv') as f:
    p.load_csv(f)

  # generate centroids for the cluster
  nclusters=12

  centroids = kmeans(list(p.postcodes.values()), nclusters=nclusters)
  # get the postcode of the centroids, as a "reference postcode" of the centroid
  centroids_pc = [p.find(c) for c in centroids]
  # use a letter to identify the clusters
  centroids_pc = [c + f'\n({chr(65 + i)})' for i, c in enumerate(centroids_pc)]
  
  # Load the data
  today = date.today()
  prices_filename = os.path.join('test_datasets', 'prices', postcode, f'{today.isoformat()}.json')
  with open(prices_filename) as f:
    prices = Prices.load(f)

  ptypes = [PropertyType.SEMI_DETACHED, PropertyType.DETACHED]
  beds = [3, 4]
  # Fill cluster of prices for the specified bedrooms and type of houses
  data = [[] for _ in range(nclusters)]
  for price in prices.raw_items:
    if price.ptype in ptypes and price.bedrooms in beds:
      cluster = find_cluster(centroids, price.coordinates)
      data[cluster].append(price.price)

  # Create the map of the cluster centroids
  map_filename = f"{postcode}_clusters_{nclusters}.png"
  if not os.path.exists(map_filename):
    markers = [Marker(label=chr(65 + i), locations=[loc]) for i, loc in enumerate(centroids)]
    with open(map_filename, 'wb') as f:
      gen_static_from_markers(map_size=MapSize(1200, 1200), out_file=f, markers=markers)

  # display boxplots
  fig = plt.figure(figsize=(14, 8))
  ax1 = fig.subplots()
  ax1.set_title(f'Prices for {[property_type2prettystr(p) for p in ptypes]} ({beds} bedrooms)')
  ax1.ticklabel_format(style='plain')
  ax1.boxplot(data, labels=centroids_pc)
  for i, p in enumerate(data, start=1):
    ax1.plot([i for _ in range(len(p))], p, 'r.', alpha=0.5)
  plt.savefig(f'{postcode}_property_boxplots.png')
  plt.show()
