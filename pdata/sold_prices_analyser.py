import json
import os

DIR='C:\\Users\\SRinco\\simone\\NewHouse\\Data'

if __name__ == '__main__':

  with open(os.path.join(DIR, 'RG14_2FB_sold_prices.json')) as f:
    j = json.load(f)

  raw_data = j['data']['raw_data']
  print(raw_data)

