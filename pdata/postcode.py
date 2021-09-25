from pdata import req

def sanitize(postcode):
  return ' '.join(postcode.split()).upper()

def to_lat_lng(postcode):

  key='17o8dysaCDrgv1c'

  p = sanitize(postcode)
  j = req.get_json('https://api.promaptools.com/service/uk/postcode-lat-lng/get/', postcode=p, key=key)
  out0 = j['output'][0]
  return out0['latitude'], out0['longitude']

if __name__ == '__main__':
  print(to_lat_lng("rg14  1nu"))
