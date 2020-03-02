from setuptools import find_packages
from setuptools import setup


setup(name='pp_middleware',
      version='0.0.1',
      packages=find_packages(),
      install_requires=[
        'grpcio==1.7.0',
        'PyJWT==1.5.3',
        'SQLAlchemy==1.1.15'
      ])
