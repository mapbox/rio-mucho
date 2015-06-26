rio-mucho
=========

Parallel processing wrapper for rasterio

|Build Status|\ |Coverage Status|

Usage
-----

1. Define a function to be applied to each window chunk. This should
   have input arguments of:

-  A list of numpy arrays (one for each file as specified in input file
   list) of shape ``({bands}, {window rows}, {window cols})``
-  A ``rasterio`` window tuple
-  A ``rasterio`` window index (``ij``)
-  A global arguments object that you can use to pass in global
   arguments

.. code:: python

    def basic_run(data, window, ij, g_args):
        return data[0]

2. Alternatively, for more flexibility, you can use a "manual read"
   where you read each raster in this function. This is useful if you
   want to read / write different window sizes (eg for pansharpening, or
   buffered window reading). Here, instead of a list of arrays, the
   function is passed an array of rasters open for reading.

.. code:: python

    def basic_run(open_files, window, ij, g_args):
        return numpy.array([f.read(window=window)[0] for f in open_files]) / g_args['divide']

For both of these, an array of identical shape to the destination window
should be returned.

3. To run, make some windows, get or make some keyword args for writing,
   and pass these and the above function into ``riomucho``: \`\`\`python
   import riomucho, rasterio, numpy

get windows from an input
=========================

with rasterio.open('/tmp/test\_1.tif') as src: windows = [[window, ij]
for ij, window in src.block\_windows()] kwargs = src.meta # since we are
only writing to 2 bands kwargs.update(count=2)

global\_args = { 'divide': 2 }

processes = 4

run it
======

with riomucho.RioMucho(['input1.tif','input2, input2.tif'],
'output.tif', basic\_run, windows=windows, global\_args=global\_args,
kwargs=kwargs) as rm:

::

    rm.run(processes)

\`\`\` - If no windows are specified, rio-mucho uses the block windows
of the first input raster - If no kwargs are specified, rio-mucho uses
the kwargs of the first input dataset to write to output - If no global
args are specified, an empty object is passed.

.. |Build Status| image:: https://travis-ci.org/mapbox/rio-mucho.svg?branch=master
   :target: https://travis-ci.org/mapbox/rio-mucho
.. |Coverage Status| image:: https://coveralls.io/repos/mapbox/rio-mucho/badge.svg?branch=setup-stuff
   :target: https://coveralls.io/r/mapbox/rio-mucho?branch=master
