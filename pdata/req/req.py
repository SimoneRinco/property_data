import requests

def get(url, **params):

  r = requests.get(url, params=params)
  if not r.ok:
    raise RuntimeError(f'GET request failed with status {r.status_code}')
  return r

def get_json(url, **params):
  r = get(url, **params)
  return r.json()


if __name__ == '__main__':

  ret1 = get('https://www.google.com/search', q='simone')
  print(ret1.url)

