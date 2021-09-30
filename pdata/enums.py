from enum import Enum
from enum import auto as eauto

class PropertyType(Enum):
  FLAT = eauto()
  TERRACED = eauto()
  SEMI_DETACHED = eauto()
  DETACHED = eauto()

PROPERTY_TYPES = [
  PropertyType.FLAT,
  PropertyType.TERRACED,
  PropertyType.SEMI_DETACHED,
  PropertyType.DETACHED
  ]

def str2property_type(str_name):
  if str_name == 'flat':
    return PropertyType.FLAT
  if str_name == 'terraced_house':
    return PropertyType.TERRACED
  if str_name == 'semi-detached_house':
    return PropertyType.SEMI_DETACHED
  if str_name == 'detached_house':
    return PropertyType.DETACHED
  raise RuntimeError(f'Invalid string {str_name}')

def property_type2str(ptype):
  if ptype == PropertyType.FLAT:
    return 'flat'
  if ptype == PropertyType.TERRACED:
    return 'terraced_house'
  if ptype == PropertyType.SEMI_DETACHED:
    return 'semi-detached_house'
  if ptype == PropertyType.DETACHED:
    return 'detached_house'
  raise RuntimeError(f'Invalid property type {ptype}')

def property_type2prettystr(ptype):
  if ptype == PropertyType.FLAT:
    return 'Flat'
  if ptype == PropertyType.TERRACED:
    return 'Terraced'
  if ptype == PropertyType.SEMI_DETACHED:
    return 'Semi Detached'
  if ptype == PropertyType.DETACHED:
    return 'Detached'
  raise RuntimeError(f'Invalid property type {ptype}')
