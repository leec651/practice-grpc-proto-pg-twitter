from grift import BaseConfig
from grift import ConfigProperty
from grift import DictLoader
from schematics.types import IntType
from schematics.types import StringType


class AppConfig(BaseConfig):
  POSTGRES_HOST = ConfigProperty(property_type=StringType())
  POSTGRES_PORT = ConfigProperty(property_type=IntType())
  POSTGRES_USER = ConfigProperty(property_type=StringType())
  POSTGRES_PASSWORD = ConfigProperty(property_type=StringType())
  POSTGRES_DB = ConfigProperty(property_type=StringType())
  JWT_SECRET = ConfigProperty(property_type=StringType())

# there are other ways to do this: https://github.com/leec651/grift/blob/dev/grift/loaders.py
dictLoader = DictLoader({
  'POSTGRES_HOST': '',
  'POSTGRES_PORT': 5432,
  'POSTGRES_USER': 'Emma',
  'POSTGRES_PASSWORD': '',
  'POSTGRES_DB': 'mydb',
  'JWT_SECRET': 'as_kd!nf98_2nf2f9_s8ff!df'
})

loaders = [dictLoader]
settings = AppConfig(loaders)

