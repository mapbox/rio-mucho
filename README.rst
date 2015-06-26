rio-mucho
=========

Parallel processing wrapper for rasterio

Usage
-----

1. Define a function to be applied to each window chunk. This should
   have input arguments of:

-  An array of of open files
-  A ``rasterio`` window tuple
-  A ``rasterio`` window index (``ij``)
-  A global arg object that you can hold global args in

   .. code:: python

       def basic_run(open_files, window, ij, g_args):
       return numpy.array([f.read(window=window)[0] for f in open_files]) / g_args['divide']

2. Make some windows, get or make some keyword args for writing, and
   pass these and the above function into ``riomucho``: \`\`\`python
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

::

    FYI

| ,--. ,------. ,--. ,--.
| \| \|,--,--, \| .-.   ,---.,--. ,--.,---. \| \| ,---. ,---. ,--,--,--.
  ,---. ,--,--, ,-' '-. \| \|\| \| \|   :\| .-. : 
  ``'  /| .-. :|  || .-. || .-. ||        || .-. :|      \'-.  .-'  |  ||  ||  ||  '--'  /\   --. \    / \   --.|  |' '-' '| '-' '|  |  |  |\   --.|  ||  |  |  |``--'``--''--'``-------'
  ``----'``--' ``----'``--' ``---' |  |-'``--``--``--' ``----'``--''--'
  ``--'``--'
| \`\`\`
