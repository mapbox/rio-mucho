# rio-mucho
Parallel processing wrapper for rasterio

## Usage

1. Define a function to be applied to each window chunk. This should have input arguments of:
 - An array of of open files
 - A `rasterio` window tuple
 - A `rasterio` window index (`ij`)
 - A global arg object that you can hold global args in
```python
def basic_run(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files]) / g_args['divide']
```

2. Make some windows, get or make some keyword args for writing, and pass these and the above function into `riomucho`:
```python
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

processes = 4

# run it
with riomucho.RioMucho(['input1.tif','input2, input2.tif'], 'output.tif', basic_run,
    windows=windows,
    global_args=global_args, 
    kwargs=kwargs) as rm:

    rm.run(processes)

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
