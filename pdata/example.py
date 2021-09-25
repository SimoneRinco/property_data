from pdkey import KEY 
import requests

if __name__ == '__main__':
  
  params = {
    'key' : KEY,
    'postcode' : 'RG14 2FB',
    'type' : 'semi-detached_house',
    'max_age' : 12}

  url =f'https://api.propertydata.co.uk/sold-prices'

  r = requests.get(url, params)

  print('=====HEADERS')
  print(r.headers)

  print('=====TEXT')
  print(r.text)

  print('=====URL')
  print(r.url)

