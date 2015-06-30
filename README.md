# rio-mucho
Parallel processing wrapper for rasterio

[![Build Status](https://travis-ci.org/mapbox/rio-mucho.svg?branch=master)](https://travis-ci.org/mapbox/rio-mucho)

## Usage

```python
with riomucho.RioMucho([{inputs}], {output}, {run function},
    windows={windows},
    global_args={global arguments}, 
    kwargs={kwargs to write}) as rios:

    rios.run({processes})
```

### Arguments

#### `inputs`

An list of file paths to open and read.

#### `output`

What file to write to.

#### `run_function`

A function to be applied to each window chunk. This should have input arguments of:

1. A data input, which can be one of:
 - A list of numpy arrays of shape (x,y,z), one for each file as specified in input file list `mode="simple_read" [default]`
 - A numpy array of shape ({_n_ input files x _n_ band count}, {window rows}, {window cols}) `mode=array_read"`
 - A list of open sources for reading `mode="manual_read"`
2. A `rasterio` window tuple
3. A `rasterio` window index (`ij`)
4. A global arguments object that you can use to pass in global arguments

This should return:

1. An output array of ({count}, {window rows}, {window cols}) shape, and of the correct data type for writing

```python
def basic_run({data}, {window}, {ij}, {global args}):
    ## do something
    return {out}
```

### Keyword arguments

#### `windows={windows}`

A list of `rasterio` window tuples to operate on. `[Default = the block windows of the first input file]`

#### `global_args={global arguments}

Since this is working in parallel, any other objects / values that you want to be accessible in the `run_function`

```python
global_args = {
    'divide_value': 2
}
```


2. To run, make some windows, get or make some keyword args for writing, and pass these and the above function into `riomucho`:
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
 - If no windows are specified, rio-mucho uses the block windows of the first input raster
 - If no kwargs are specified, rio-mucho uses the kwargs of the first input dataset to write to output
 - If no global args are specified, an empty object is passed.
