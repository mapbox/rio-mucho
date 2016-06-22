import os
from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='rio-mucho',
      version='0.2.0',
      description=u"Windowed multiprocessing wrapper for rasterio",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author=u"Damon Burgett",
      author_email='damon@mapbox.com',
      url='https://github.com/mapbox/rio-mucho',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=read('requirements.txt').splitlines(),
      extras_require={
          'test': ['pytest', 'pytest-cov', 'coveralls'],
      }
      )
