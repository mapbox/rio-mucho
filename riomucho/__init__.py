from __future__ import with_statement
from multiprocessing import Pool
import rasterio as rio
import numpy as np
import click

 
work_func = None
global_args = None
srcs = None
 
 
def main_worker(inpaths, g_work_func, g_args):
    """"""
    global work_func
    global global_args
    global srcs
    work_func = g_work_func
    global_args = g_args
    try:
        srcs = [rio.open(i) for i in inpaths]
    except:
        return 
 
def reader_worker(args):
    window, ij = args
    return work_func(srcs, window, ij, global_args), window


def getKwargs(input):
    with rio.open(input) as src:
        return kwargs

def getWindows(input):
    with rio.open(input) as src:
        return [[window, ij] for ij, window in src.block_windows()]

class RioMucho:
    def __init__(self, inpaths, outpath, run_function, **kwargs):
        self.inpaths = inpaths
        if not 'windows' in kwargs:
            self.windows = getWindows(inpaths[0])
        else:
            self.windows = kwargs['windows']

        if not 'kwargs' in kwargs:
            self.kwargs = getKwargs(inpaths[0])
        else:
            self.kwargs = kwargs['kwargs']

        if not 'global_args' in kwargs:
            self.global_args = {}
        else:
            self.global_args = kwargs['global_args']

        self.outpath = outpath
        self.run_function = run_function
    def __enter__(self):
        return self
    def __exit__(self, ext_t, ext_v, trace):
        if ext_t:
            click.echo("in __exit__")

    def run(self, processes=4):
        pool = Pool(processes, main_worker, (self.inpaths, self.run_function, self.global_args))
    
        ##shh
        self.kwargs['transform'] = self.kwargs['affine']

        ## Open an output file, work through the function in parallel, and write out the data
        with rio.open(self.outpath, 'w', **self.kwargs) as dst:   
            for data, window in pool.imap_unordered(reader_worker, self.windows):
                dst.write(data, window=window)

        pool.close()
        pool.join()

        return


if __name__ == '__main__':
    RioMucho()
