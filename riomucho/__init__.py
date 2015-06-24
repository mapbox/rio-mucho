from __future__ import with_statement
from multiprocessing import Pool
import rasterio as rio
import numpy as np

 
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
 
def read_write_multiple(inpaths, outpath, run_function, windows, g_args, kwargs, processes=4):
    """Read, process, and write windows from multiple rasters in parallel"""

    ## Create a pool and set globals
    pool = Pool(processes, main_worker, (inpaths, run_function, g_args))

    kwargs['transform'] = kwargs['affine']

    ## Open an output file, work through the function in parallel, and write out the data
    try:
        with rio.open(outpath, 'w', **kwargs) as dst:   
            for data, window in pool.imap_unordered(reader_worker, windows):
                dst.write(data, window=window)
        pool.close()
        pool.join()
        return True
    except:
        pool.close()
        pool.join()
        return False
if __name__ == '__main__':
    read_write_multiple()
