from setuptools import find_packages
from setuptools import setup


setup(name='pp_config',
      version='0.0.1',
      packages=find_packages(),
      install_requires=[
        'grift==0.6.0',
        'schematics==1.1.1'
      ]
)