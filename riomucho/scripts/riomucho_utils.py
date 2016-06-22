import rasterio as rio
import numpy as np
import click


def getOptions(input):
    with rio.open(input) as src:
        return src.profile


def getWindows(input):
    with rio.open(input) as src:
        return [[window, ij] for ij, window in src.block_windows()]

def array_stack(arrays):
    shapes = np.array([a.shape for a in arrays])

    if not np.all(np.roll(shapes[:,1:], 1, axis=0) == shapes[:,1:]):
        raise ValueError('All input arrays must have the same height and width for this mode')

    width = arrays[0].shape[-1]
    height = arrays[0].shape[-2]

    return np.array(
        [a for subarray in arrays for a in subarray]
        ).reshape(shapes[:,0].sum(), height, width)