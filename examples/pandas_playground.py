import pandas

import math
import collections

Data = collections.namedtuple('Data', 'k1 k2 v1 v2')


if __name__ == '__main__':

  d = {
    'k1': ['a', 'b', 'c'] * 3,
    'k2': [math.floor(i/5) for i in range(9)],
    'v1': [3 * i for i in range(9)],
    'v2': [2 * i for i in range(9)]
    }

  df = pandas.DataFrame(d)
  print(df)

  df_grouped = df.groupby(['k1', 'k2']).mean()
  print(df_grouped)

  # data frame from named tuple

  d2 = [Data(**{k : v[i] for k, v in d.items()}) for i in range(9)]
  df2 = pandas.DataFrame(d2)
  print(df2)

  # Now I want to group by k1 and k2 but average only v1
  df_grouped2 = df2.groupby(['k1', 'k2'])
  print(df_grouped2)
  df_grouped2_mean = df_grouped2.agg({'v1' : 'mean'})
  print(df_grouped2_mean)
  print(type(df_grouped2_mean))

  # get 'v1' for entry with key k1='a' and k2=0
  row = df_grouped2_mean.at[('a', 0), 'v1']
  print(row)

  # Update df2 setting the value of 'v1' equal to the mean for the same key

  for index, row in df2.iterrows():
    print(index)
    print(row)
    print(row['v1'])
    row['v1'] = df_grouped2_mean.at[(row['k1'], row['k2']), 'v1']
    df2.loc[index] = row

  print(df2)





