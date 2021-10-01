from pdata.postcode import sanitize as postcode_sanitize

from collections import namedtuple
import math

EARTH_RADIUS = 6371e3

LatLng = namedtuple('LatLng', ['lat', 'lng'])

CartesianCoo = namedtuple('CartesianCoo', ['x', 'y', 'z'])

def dict2coo(d):
  """It looks for 'lat' and 'lng' keywords in the dict
  """
  return LatLng(lat=float(d['lat']), lng=float(d['lng']))


def to_radiants(degrees):
  return degrees * math.pi / 180


def to_degrees(rad):
  return rad * 180 / math.pi


def to_cartesian(latlng):

  lat = to_radiants(latlng.lat)
  lng = to_radiants(latlng.lng)

  return CartesianCoo(
    x=EARTH_RADIUS * math.cos(lat) * math.cos(lng),
    y=EARTH_RADIUS * math.cos(lat) * math.sin(lng),
    z=EARTH_RADIUS * math.sin(lat)
    )


def to_latlng(cartesian_coo):
  # Assume the point is on the surface of the earth or very very close
  lat_rad = math.asin(cartesian_coo.z / EARTH_RADIUS)
  lng_rad = math.asin(cartesian_coo.y / (EARTH_RADIUS * math.cos(lat_rad)))

  return LatLng(lat=to_degrees(lat_rad), lng=to_degrees(lng_rad))


def distance(p1, p2):

  lat1 = to_radiants(p1.lat)
  lat2 = to_radiants(p2.lat)

  lng1 = to_radiants(p1.lng)
  lng2 = to_radiants(p2.lng)

  delta_lat = lat1 - lat2
  delta_lng = lng1 - lng2

  slat = math.sin(delta_lat/2)
  slng = math.sin(delta_lng/2)

  a = slat*slat + math.cos(lat1) * math.cos(lat2) * slng*slng
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  ret = EARTH_RADIUS * c

  # This approximation can be used instead
  # ret_approx = EARTH_RADIUS * math.sqrt(delta_lat**2 + (math.cos(lat1) * delta_lng)**2)
  return ret


class PostcodeFinder(object):

  def __init__(self):
    self.postcodes = {}

  def load_csv(self, reader):
    for line in reader:
      if line['In Use?'] == "Yes":
        self.postcodes[postcode_sanitize(line['Postcode'])] = \
          LatLng(
            lat=float(line['Latitude']),
            lng=float(line['Longitude'])
            )

  def find(self, lat_lng):
    ret = ''
    min_dist = 1e100

    for postcode, postcode_center in self.postcodes.items():
      d = distance(lat_lng, postcode_center)
      if d < min_dist:
        min_dist = d
        ret = postcode

    return ret, min_dist


def get_centroid(latlng):

  size = len(latlng)

  x = [0 for _ in range(size)]
  y = [0 for _ in range(size)]
  z = [0 for _ in range(size)]

  for i, ll in enumerate(latlng):
    cc = to_cartesian(ll)
    x[i] = cc.x
    y[i] = cc.y
    z[i] = cc.z

  cart_coo = CartesianCoo(
    x=math.fsum(x) / size,
    y=math.fsum(y) / size,
    z=math.fsum(z) / size
    )

  return to_latlng(cart_coo)


def kmeans(latlng, nclusters, max_iter=10):
  """latlng: iterable of LatLng
  Returns a list of nclusters elements containing the centroids (LatLng)
  """

  npoints = len(latlng)

  if npoints < nclusters:
    raise RuntiRuntimeError('kmeans failed: less points than number of clusters')

  # initialise centroids
  centroids = [LatLng(lat=0, lng=0) for _ in range(nclusters)]
  s = math.floor(npoints / nclusters)
  for i in range(nclusters - 1):
    centroids[i] = get_centroid(latlng[s*i : s*(i+1)])
    centroids[-1] = get_centroid(latlng[s*(nclusters-1) :])

  def find_cluster(centroids_, ll_):
    ret = 0
    min_dist = distance(centroids_[0], ll_)
    for i, c in enumerate(centroids_[1:], start=1):
      d = distance(c, ll)
      if d < min_dist:
        min_dist = d
        ret = i
    return ret

  # first assignment
  cluster_ids = [-1 for _ in range(npoints)]
  for i, ll in enumerate(latlng):
    cluster_ids[i] = find_cluster(centroids, ll)

  for niter in range(max_iter):
    # recalculate centroids
    for i in range(nclusters):
      centroids[i] = get_centroid([ll for (j, ll) in zip(cluster_ids, latlng) if j == i])
    # reassign points to new centroids
    any_change = False
    for i, ll in enumerate(latlng):
      old_cluster = cluster_ids[i]
      cluster_ids[i] = find_cluster(centroids, ll)
      if old_cluster != cluster_ids[i]:
        any_change = True
    if not any_change:
      break

  return centroids



if __name__ == "__main__":

  import csv

  postcode_finder = PostcodeFinder()
  with open("postcodes/RG14.csv") as f:
    r = csv.DictReader(f)
    postcode_finder.load_csv(r)


  print(postcode_finder.find(LatLng(51.40647170213218, -1.3269289786844287)))

  centroids = kmeans(list(postcode_finder.postcodes.values()), nclusters=16)

  print(centroids)
  
  from pdata.maps.mapgen import Marker, MarkerSize, MapSize, gen_static_from_markers

  marker = Marker(size=MarkerSize.SMALL, locations=centroids)
  size = MapSize(800, 800)

  with open("RG14_centroids.png", 'wb') as f:
    gen_static_from_markers(map_size=size, out_file=f, markers=[marker])






