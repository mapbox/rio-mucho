from __future__ import with_statement
from multiprocessing import Pool
import rasterio as rio
import numpy as np
import click


def getKwargs(input):
    with rio.open(input) as src:
        return src.meta


def getWindows(input):
    with rio.open(input) as src:
        return [[window, ij] for ij, window in src.block_windows()]

def testUtils():
    return "yo"

def readArrayStacker(arrays):
    width = arrays[0].shape[-1]
    height = arrays[0].shape[-2]

    return np.array(
        [a for subarray in arrays for a in subarray]
        ).reshape(sum(
            [a.shape[0] for a in arrays]
            ), height, width)