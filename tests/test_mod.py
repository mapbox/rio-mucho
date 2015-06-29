import riomucho
import rasterio
import make_testing_data
import click, numpy
import numpy as np

make_testing_data.makeTesting('/tmp/test_1.tif', 512, 256, 1)
make_testing_data.makeTesting('/tmp/test_2.tif', 512, 256, 1)

def read_function_manual(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files])

def runRioMuchoManual():
    with rasterio.open('/tmp/test_1.tif') as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        kwargs = src.meta
        kwargs.update(count=2)

    with riomucho.RioMucho(['/tmp/test_1.tif','/tmp/test_2.tif'], '/tmp/test_xyz_out.tif', read_function_manual,
        windows=windows,
        global_args={}, 
        kwargs=kwargs,
        manual_read=True) as rm:

        rm.run(4)

    return True

def test_riomucho_manual():
    assert runRioMuchoManual() == True

def read_function_simple(data, window, ij, g_args):
    return data[0]

def runRioMuchoSimple():
    with riomucho.RioMucho(['/tmp/test_1.tif'], '/tmp/test_xyz_out.tif', read_function_simple) as rm:
        rm.run(4)

    return True

def test_riomucho_simple():
    assert runRioMuchoSimple() == True

def test_arraystack():
    t_width = int(np.random.rand() * 100) + 1
    t_height = int(np.random.rand() * 100) + 1
    t_inputs = int(np.random.rand() * 4 + 1)
    t_counts = [int(np.random.rand() * 3 + 1) for i in range(t_inputs)]
    shape_expected = tuple((sum(t_counts * t_inputs), t_height, t_width))
    t_array_list = [np.zeros((i, t_height, t_width)) for i in t_counts]

    a = riomucho.utils.readArrayStacker(t_array_list)
    assert a.shape == tuple((sum(t_counts), t_height, t_width))