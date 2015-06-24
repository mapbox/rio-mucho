# rio-mucho
Parallel processing wrapper for rasterio

## Usage

1. Define a function to be applied to each window chunk. This should arguments of:
 - An array of of open files
 - A `rasterio` window tuple
 - A `rasterio` window index (`ij`)
 - A global arg object that you can hold global args in
```
def basic_run(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files]) / g_args['divide']
```

2. Make some windows, get or make some keyword args for writing, and pass these and the above function into `riomucho`:
```
import riomucho, rasterio, numpy

# get windows from an input
with rasterio.open('/tmp/test_1.tif') as src:
    windows = [[window, ij] for ij, window in src.block_windows()]
    kwargs = src.meta
    # since we are only writing to 2 bands
    kwargs.update(count=2)

global_args = {
    'divide': 2
}

# run it
riomucho.read_write_multiple(['/tmp/test_1.ti','/tmp/test_2.tif'], '/tmp/test_3_out.tif', basic_run, windows, global_args, kwargs, 4)

```
FYI
```
                                                                                                
,--.        ,------.                        ,--.                                         ,--.   
|  |,--,--, |  .-.  \  ,---.,--.  ,--.,---. |  | ,---.  ,---. ,--,--,--. ,---. ,--,--, ,-'  '-. 
|  ||      \|  |  \  :| .-. :\  `'  /| .-. :|  || .-. || .-. ||        || .-. :|      \'-.  .-' 
|  ||  ||  ||  '--'  /\   --. \    / \   --.|  |' '-' '| '-' '|  |  |  |\   --.|  ||  |  |  |   
`--'`--''--'`-------'  `----'  `--'   `----'`--' `---' |  |-' `--`--`--' `----'`--''--'  `--'   
                                                       `--'                                     
```
