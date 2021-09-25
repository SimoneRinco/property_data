from mkey import KEY 
import requests

if __name__ == '__main__':
  
  params = {
    'key' : KEY,
    'center' : '51.40552,-1.30012',
    'zoom' : '16',
    'size' : '600x600',
    'markers' : [
      'size:mid|color:green|label:A|51.40513200,-1.29996670|51.40583520,-1.30071500',
      'size:mid|color:yellow|label:B|51.40498780,-1.30035410|51.40603090,-1.29990990',
      ]
    }

  url ='https://maps.googleapis.com/maps/api/staticmap'

  r = requests.get(url, params)

  #print('=====HEADERS')
  #print(r.headers)

  #print('=====TEXT')
  #print(r.text)

  #print('=====URL')
  #print(r.url)

  with open('example3.png', 'wb') as f:
    for chunk in r.iter_content(chunk_size=128):
      f.write(chunk)