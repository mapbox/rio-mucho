"""TODO
"""

from __future__ import with_statement
from multiprocessing import Pool
import rasterio as rio
from rasterio.transform import guard_transform
import numpy as np
import click
import riomucho.scripts.riomucho_utils as utils
from riomucho.single_process_pool import MockTub
import traceback


work_func = None
global_args = None
srcs = None


def main_worker(inpaths, g_work_func, g_args):
    """TODO"""
    global work_func
    global global_args
    global srcs
    work_func = g_work_func
    global_args = g_args
    srcs = [rio.open(i) for i in inpaths]


def manualRead(args):
    """TODO"""
    window, ij = args
    return work_func(srcs, window, ij, global_args), window


def arrayRead(args):
    """TODO"""
    window, ij = args
    return work_func(utils.array_stack(
        [src.read(window=window) for src in srcs]),
        window, ij, global_args), window


def simpleRead(args):
    """TODO"""
    window, ij = args
    return work_func([src.read(window=window) for src in srcs], window, ij, global_args), window


class RioMucho:
    """TODO
    """

    def __init__(self, inpaths, outpath, run_function, **kwargs):
        """TODO
        """
        self.inpaths = inpaths
        self.outpath = outpath
        self.run_function = run_function

        if 'mode' not in kwargs or kwargs['mode'] == 'simple_read':
            self.mode = 'simple_read'
        elif kwargs['mode'] == 'array_read':
            self.mode = 'array_read'
        elif kwargs['mode'] == 'manual_read':
            self.mode = 'manual_read'
        else:
            raise ValueError('mode must be one of: ["simple_read", "manual_read", "array_read"]')

        if 'windows' not in kwargs:
            self.windows = utils.getWindows(inpaths[0])
        else:
            self.windows = kwargs['windows']

        if 'options' not in kwargs:
            self.options = utils.getOptions(inpaths[0])
        else:
            self.options = kwargs['options']

        if 'global_args' not in kwargs:
            self.global_args = {}
        else:
            self.global_args = kwargs['global_args']

    def __enter__(self):
        return self

    def __exit__(self, ext_t, ext_v, trace):
        pass

    def run(self, processes=4):
        """TODO"""
        if processes == 1:
            self.pool = MockTub(main_worker, (self.inpaths, self.run_function, self.global_args))
        else:
            self.pool = Pool(processes, main_worker, (self.inpaths, self.run_function, self.global_args))

        self.options['transform'] = guard_transform(self.options['transform'])

        if self.mode == 'manual_read':
            reader_worker = manualRead
        elif self.mode == 'array_read':
            reader_worker = arrayRead
        else:
            reader_worker = simpleRead

        # Open an output file, work through the function in parallel,
        # and write out the data.
        with rio.open(self.outpath, 'w', **self.options) as dst:
            for data, window in self.pool.imap_unordered(reader_worker, self.windows):
                dst.write(data, window=window)

        self.pool.close()
        self.pool.join()
