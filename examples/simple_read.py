import riomucho
import numpy

# example simple read

### basic function
## takes an array, and sets any value above the mean to the max, the rest to 0
def read_function(data, window, ij, g_args):
    output = (data[0] > numpy.mean(data[0])).astype(data[0].dtype) * data[0].max()
    return output

## open w/ simple read mode, and work in parallel
with riomucho.RioMucho(
    ['/tmp/test_1.tif'],
    '/tmp/test_z_out.tif',
    read_function,
    global_args={}) as rm:

    rm.run(4)