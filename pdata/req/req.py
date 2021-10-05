import requests

def get(url, **params):

  r = requests.get(url, params=params)
  if r.ok:
    return r

  # Something went wrong: try to get the error if possible
  try:
    j = r.json()
    error_msg = j['message']
  except:
    error_msg = 'unknown error'

  raise RuntimeError(f'GET request failed with status {r.status_code}, error message: {error_msg}')


def get_json(url, **params):
  r = get(url, **params)
  return r.json()


# Used to be 2s before removal of the API throttle.
MIN_TIME_BETWEEN_API_CALLS = 0.25


if __name__ == '__main__':

  ret1 = get('https://www.google.com/search', q='simone')
  print(ret1.url)

