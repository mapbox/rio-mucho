"""Utility functions
"""

import rasterio
import numpy as np


def getOptions(input):
    """Get a source's profile"""
    with rasterio.open(input) as src:
        return src.profile


def getWindows(input):
    """Get a source's windows"""
    with rasterio.open(input) as src:
        return [[window, ij] for ij, window in src.block_windows()]


def array_stack(arrays):
    """Stack arrays"""
    shapes = np.array([a.shape for a in arrays])

    if not np.all(np.roll(shapes[:, 1:], 1, axis=0) == shapes[:, 1:]):
        raise ValueError(
            "All input arrays must have the same height and width for this mode"
        )

    width = arrays[0].shape[-1]
    height = arrays[0].shape[-2]

    return np.array([a for subarray in arrays for a in subarray]).reshape(
        shapes[:, 0].sum(), height, width
    )
