
from pdata.enums import PropertyType

PLOT_COLORS = {
  PropertyType.FLAT : [
    None,
    'peachpuff',
    'peru',
    'sienna',
    None,
    None],
  PropertyType.TERRACED : [
    None,
    'bisque',
    'tan',
    'orange',
    'darkorange', None],
  PropertyType.SEMI_DETACHED : [
    None,
    None,
    'lavender',
    'skyblue',
    'steelblue',
    'dodgerblue'],
  PropertyType.DETACHED : [
    None,
    None,
    'yellow',
    'lawngreen',
    'lightgreen',
    'lime',
    'forestgreen',
    'darkgreen'],
  }

def get_color(ptype, nbedrooms):

  clist = PLOT_COLORS[ptype]
  if nbedrooms < len(clist):
    return clist[nbedrooms]
  return None
