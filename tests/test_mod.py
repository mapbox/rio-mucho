import riomucho
import rasterio
import make_testing_data
import click, numpy

make_testing_data.makeTesting('/tmp/test_1.tif', 512, 256, 1)
make_testing_data.makeTesting('/tmp/test_2.tif', 512, 256, 1)

def read_function(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files])

def runRioMucho():
    with rasterio.open('/tmp/test_1.tif') as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        kwargs = src.meta
        kwargs.update(count=2)

    with riomucho.RioMucho(['/tmp/test_1.tif','/tmp/test_2.tif'], '/tmp/test_z_out.tif', read_function,
        windows=windows,
        global_args={}, 
        kwargs=kwargs,
        manual_read=True) as rm:

        rm.run(4)

    return True

def run_test():
    assert runRioMucho() == True