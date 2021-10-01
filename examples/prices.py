from pdata.postcode import Postcodes
from pdata.coordinates import kmeans, find_cluster
from pdata.req.prices import Prices
from pdata.enums import PropertyType, property_type2prettystr
from pdata.maps.mapgen import Marker, MapSize, gen_static_from_markers

import matplotlib.pyplot as plt

import json
import os

"""Example on how to use the "prices" API, or visualise
prices previously downloaded using the API
"""

if __name__ == '__main__':

  # load postcodes in Newbury
  p = Postcodes()
  with open('postcodes/RG14.csv') as f:
    p.load_csv(f)

  # generate centroids for the cluster
  nclusters=12

  centroids = kmeans(list(p.postcodes.values()), nclusters=nclusters)
  # get the postcode of the centroids, as a "reference postcode" of the centroid
  centroids_pc = [p.find(c) for c in centroids]
  # use a letter to identify the clusters
  centroids_pc = [c + f'\n({chr(65 + i)})' for i, c in enumerate(centroids_pc)]
  
  # Load or get all the prices from Property Data
  prices_filename = 'test_datasets/prices/RG14/20211001.json'
  if os.path.exists(prices_filename):
    with open(prices_filename) as f:
      prices = Prices.load(f)
  else:
    j = Prices.req(postcode="RG14")
    # Save it, so we don't call the API twice
    with open(prices_filename, 'w') as f:
      json.dump(j, f)
    prices = Prices.Data(j)

  ptypes = [PropertyType.SEMI_DETACHED]
  beds = [3]
  # Fill cluster of prices for 3 bedrooms, semi detached houses
  data = [[] for _ in range(nclusters)]
  for price in prices.raw_items:
    if price.ptype in ptypes and price.bedrooms in beds:
      cluster = find_cluster(centroids, price.coordinates)
      data[cluster].append(price.price)

  # display boxplots
  fig = plt.figure(figsize=(14, 8))
  ax1 = fig.subplots()
  ax1.set_title(f'Prices for {[property_type2prettystr(p) for p in ptypes]} ({beds} bedrooms)')
  ax1.ticklabel_format(style='plain')
  ax1.boxplot(data, labels=centroids_pc)
  for i, p in enumerate(data, start=1):
    ax1.plot([i for _ in range(len(p))], p, 'r.', alpha=0.5)
  plt.savefig('RG14_property_boxplots.png')
  plt.show()

  # Create the map of the cluster centroids
  map_filename = f"RG14_clusters_{nclusters}.png"
  if not os.path.exists(map_filename):
    markers = [Marker(label=chr(65 + i), locations=[loc]) for i, loc in enumerate(centroids)]
    with open(map_filename, 'wb') as f:
      gen_static_from_markers(map_size=MapSize(1200, 1200), out_file=f, markers=markers)



