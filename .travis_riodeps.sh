#!/usr/bin/env bash
#
# Conditionally download a wheelset satisfying Rasterio's dependencies to 
# speed up builds.

set -e

WHEELHOUSE=$HOME/wheelhouse

if [[ ! -e "$WHEELHOUSE/rasterio-$RASTERIO_VERSION-cp27-none-linux_x86_64.whl" ]]; then
    echo "Downloading speedy wheels..."
    curl -L https://github.com/mapbox/rasterio/releases/download/$RASTERIO_VERSION/rasterio-travis-wheels-$TRAVIS_PYTHON_VERSION.tar.gz > /tmp/wheelhouse.tar.gz
    echo "Extracting speedy wheels..."
    tar -xzvf /tmp/wheelhouse.tar.gz -C $HOME
else
    echo "Using existing wheelhouse."
fi
