import riomucho
import rasterio
import make_testing_data
import click, numpy

make_testing_data.makeTesting('/tmp/test_1.tif', 1048, 256, 1)
make_testing_data.makeTesting('/tmp/test_2.tif', 1048, 256, 1)

def basic_run(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files])

def f():
    with rasterio.open('/tmp/test_1.tif') as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        kwargs = src.meta
        kwargs.update(count=2)
    return riomucho.read_write_multiple(['/tmp/test_1.ti','/tmp/test_2.tif'], '/tmp/test_3_out.tif', basic_run, windows, {}, kwargs, 4)

def test_function():
    assert f() == True