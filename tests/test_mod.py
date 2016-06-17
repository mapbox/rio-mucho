import riomucho
import rasterio
import make_testing_data
import click, numpy
import pytest

make_testing_data.makeTesting('/tmp/test_1.tif', 512, 256, 1)
make_testing_data.makeTesting('/tmp/test_2.tif', 512, 256, 1)

def read_function_manual(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files])

def runRioMuchoManual():
    with rasterio.open('/tmp/test_1.tif') as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        options = src.meta
        options.update(count=2)

    with riomucho.RioMucho(['/tmp/test_1.tif','/tmp/test_2.tif'], '/tmp/test_xyz_out.tif', read_function_manual,
        windows=windows,
        global_args={}, 
        options=options,
        mode='manual_read') as rm:

        rm.run(4)

    return True

def test_riomucho_manual():
    assert runRioMuchoManual() == True

def read_function_simple(data, window, ij, g_args):
    return data[0]

def runRioMuchoSimple():
    with riomucho.RioMucho(['/tmp/test_1.tif'], '/tmp/test_xyz_out.tif', read_function_simple) as rm:
        rm.run(1)

    return True

def test_riomucho_simple():
    assert runRioMuchoSimple() == True

def read_function_arrayread(data, window, ij, g_args):
    return data

def runRioMuchoArrayRead():
    with rasterio.open('/tmp/test_1.tif') as src:
        options = src.meta
        options.update(count=2)

    with riomucho.RioMucho(['/tmp/test_1.tif', '/tmp/test_2.tif'], '/tmp/test_xyz_out.tif', read_function_arrayread,
        mode='array_read', options=options) as rm:
        rm.run(4)

    return True

def test_riomucho_arrayread():
    assert runRioMuchoArrayRead() == True

def test_arraystack():
    t_array_list, expected_shape = make_testing_data.makeRandomArrays()

    stacked = riomucho.utils.array_stack(t_array_list)
    assert stacked.shape == expected_shape

def test_bad_arraystack():
    t_array_list, expected_shape = make_testing_data.makeRandomArrays()

    t_array_list.append(numpy.zeros((1, 1, 1)))

    with pytest.raises(ValueError):
        riomucho.utils.array_stack(t_array_list)