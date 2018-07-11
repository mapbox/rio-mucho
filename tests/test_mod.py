import riomucho
import rasterio
import make_testing_data
import click
import numpy
import pytest

from rasterio.errors import RasterioIOError

make_testing_data.makeTesting('/tmp/test_1.tif', 512, 256, 1)
make_testing_data.makeTesting('/tmp/test_2.tif', 512, 256, 1)


def read_function_manual(open_files, window, ij, g_args):
    return numpy.array([f.read(window=window)[0] for f in open_files])


def test_riomucho_manual():
    with rasterio.open('/tmp/test_1.tif') as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        options = src.meta
        options.update(count=2)

    with riomucho.RioMucho(['/tmp/test_1.tif', '/tmp/test_2.tif'], '/tmp/test_xyz_out.tif', read_function_manual,
        windows=windows,
        global_args={}, 
        options=options,
        mode='manual_read') as rm:

        rm.run(4)

    with rasterio.open('/tmp/test_1.tif') as inputsrc:
        with rasterio.open('/tmp/test_xyz_out.tif') as outputsrc:
            assert inputsrc.checksum(1) == outputsrc.checksum(1)


def read_function_simple(data, window, ij, g_args):
    data[0][:10, :10] = 0
    return data[0]


def test_riomucho_simple():
    with riomucho.RioMucho(['/tmp/test_1.tif'], '/tmp/test_xyz_out.tif', read_function_simple) as rm:
        rm.run(1)

    with rasterio.open('/tmp/test_xyz_out.tif') as outputsrc:
        assert numpy.sum(outputsrc.read(1)[:10, :10] != 0) == 0


def test_riomucho_simple_fail():
    with pytest.raises(RasterioIOError):
        with riomucho.RioMucho(['/tmp/test_999.tif'], '/tmp/test_xyz_out.tif', read_function_simple) as rm:
            rm.run(1)


def read_function_arrayread(data, window, ij, g_args):
    return data


def test_riomucho_arrayread():
    with rasterio.open('/tmp/test_1.tif') as src:
        options = src.profile
        options.update(count=2)

    with riomucho.RioMucho(['/tmp/test_1.tif', '/tmp/test_2.tif'], '/tmp/test_xyz_out.tif', read_function_arrayread,
        mode='array_read', options=options) as rm:
        rm.run(4)

    with rasterio.open('/tmp/test_1.tif') as inputsrc1:
        with rasterio.open('/tmp/test_2.tif') as inputsrc2:
            with rasterio.open('/tmp/test_xyz_out.tif') as outputsrc:
                assert inputsrc1.checksum(1) == outputsrc.checksum(1)
                assert inputsrc2.checksum(1) == outputsrc.checksum(2)


def test_riomucho_readmode_fail():
    with pytest.raises(ValueError):
        with riomucho.RioMucho(['/tmp/test_1.tif',], '/tmp/test_xyz_out.tif', read_function_arrayread,
            mode='mucho_gusto') as rm:
            rm.run(4)


def test_arraystack():
    t_array_list, expected_shape = make_testing_data.makeRandomArrays()

    stacked = riomucho.utils.array_stack(t_array_list)
    assert stacked.shape == expected_shape


def test_bad_arraystack():
    t_array_list, expected_shape = make_testing_data.makeRandomArrays()

    t_array_list.append(numpy.zeros((1, 1, 1)))

    with pytest.raises(ValueError):
        riomucho.utils.array_stack(t_array_list)


def test_pool_worker_exceptions(tmpdir):
    with rasterio.open('/tmp/test_1.tif') as src:
        options = src.profile
        options.update(count=2)

    def fail(data, window, ij, g_args):
        return data * (1 / 0)

    with riomucho.RioMucho(['/tmp/test_1.tif', '/tmp/test_2.tif'], str(tmpdir.join('output.tif')), fail,
            mode='array_read', options=options) as rm:
        with pytest.raises(riomucho.MuchoChildError) as excinfo:
            rm.run(4)

        assert "ZeroDivisionError" in str(excinfo.value)


def test_job_decorator():
    """Exception in a job is captured"""
    @riomucho.job
    def foo(*args, **kwargs):
        return 1 / 0

    with pytest.raises(riomucho.MuchoChildError) as excinfo:
        foo()

    assert "ZeroDivisionError" in str(excinfo.value)
