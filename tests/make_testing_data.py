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

if __name__ == '__main__':
    makeTesting()
