import rasterio
from rasterio import Affine
import numpy as np

def makeTesting(output, size, windowsize, bands):
    kwargs = {'count': bands,
        'crs': {'init': u'epsg:3857'},
        'dtype': 'uint8',
        'driver': u'GTiff',
        'transform': Affine(4.595839562240513, 0.0, -13550756.3744,
            0.0, -4.595839562240513, 6315533.02503),
        'height': size,
        'width': size,
        'compress': 'lzw',
        'blockxsize': windowsize,
        'blockysize': windowsize,
        'tiled': True
        }

    randArr = np.array([
        (np.random.rand(size, size) * 255).astype(np.uint8) for i in range(bands)
        ])

    with rasterio.open(output, 'w', **kwargs) as dst:
        dst.write(randArr)

def makeRandomArrays(maxsize=100):
    width = int(np.random.rand() * maxsize) + 1
    height = int(np.random.rand() * maxsize) + 1
    inputs = int(np.random.rand() * 4 + 1)
    counts = [int(np.random.rand() * 3 + 1) for i in range(inputs)]
    shape_expected = tuple((sum(counts * inputs), height, width))
    array_list = [np.zeros((i, height, width)) for i in counts]
    expected_shape = tuple((sum(counts), height, width))

    return array_list, expected_shape


if __name__ == '__main__':
    makeTesting()
    makeRandomArrays
