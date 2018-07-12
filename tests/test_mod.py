import riomucho
import rasterio
import click
import numpy
import pytest

from rasterio.errors import RasterioIOError


def read_function_manual(open_files, window, ij, g_args):
    """A user function for testing"""
    return numpy.array([f.read(window=window)[0] for f in open_files])


def test_riomucho_manual(tmpdir, test_1_tif, test_2_tif):
    """Distribution of a manual read user function succeeds"""
    with rasterio.open(str(test_1_tif)) as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        options = src.meta
        options.update(count=2)

    with riomucho.RioMucho(
        [str(test_1_tif), str(test_2_tif)],
        str(tmpdir.join("test_xyz_out.tif")),
        read_function_manual,
        windows=windows,
        global_args={},
        options=options,
        mode="manual_read",
    ) as rm:
        rm.run(4)

    with rasterio.open(str(test_1_tif)) as inumpyutsrc:
        with rasterio.open(str(tmpdir.join("test_xyz_out.tif"))) as outputsrc:
            assert inumpyutsrc.checksum(1) == outputsrc.checksum(1)


def read_function_simple(data, window, ij, g_args):
    """A user function for testing"""
    data[0][:10, :10] = 0
    return data[0]


def test_riomucho_simple(tmpdir, test_1_tif):
    """Distribution of a simple user function works"""
    with riomucho.RioMucho(
        [str(test_1_tif)], str(tmpdir.join("test_xyz_out.tif")), read_function_simple
    ) as rm:
        rm.run(1)

    with rasterio.open(str(tmpdir.join("test_xyz_out.tif"))) as outputsrc:
        assert numpy.sum(outputsrc.read(1)[:10, :10] != 0) == 0


def test_riomucho_simple_fail(tmpdir):
    """Invalid source file fails normally"""
    with pytest.raises(RasterioIOError):
        with riomucho.RioMucho(
            ["test_999.tif"], str(tmpdir.join("test_xyz_out.tif")), read_function_simple
        ) as rm:
            rm.run(1)


def read_function_arrayread(data, window, ij, g_args):
    """An array reading user function for testing"""
    return data


def test_riomucho_arrayread(tmpdir, test_1_tif, test_2_tif):
    """Distribution of an array reading user function works"""
    with rasterio.open(str(test_1_tif)) as src:
        options = src.profile
        options.update(count=2)

    with riomucho.RioMucho(
        [str(test_1_tif), str(test_2_tif)],
        str(tmpdir.join("test_xyz_out.tif")),
        read_function_arrayread,
        mode="array_read",
        options=options,
    ) as rm:
        rm.run(4)

    with rasterio.open(str(test_1_tif)) as inumpyutsrc1:
        with rasterio.open(str(test_2_tif)) as inumpyutsrc2:
            with rasterio.open(str(tmpdir.join("test_xyz_out.tif"))) as outputsrc:
                assert inumpyutsrc1.checksum(1) == outputsrc.checksum(1)
                assert inumpyutsrc2.checksum(1) == outputsrc.checksum(2)


def test_riomucho_readmode_fail(tmpdir, test_1_tif):
    """Invalid mode fails with ValueError"""
    with pytest.raises(ValueError):
        with riomucho.RioMucho(
            [str(test_1_tif)],
            str(tmpdir.join("test_xyz_out.tif")),
            read_function_arrayread,
            mode="mucho_gusto",
        ) as rm:
            rm.run(4)


def makeRandomArrays(maxsize=100):
    """Make random arrays"""
    # TODO: hypothesize this?
    width = int(numpy.random.rand() * maxsize) + 1
    height = int(numpy.random.rand() * maxsize) + 1
    inumpyuts = int(numpy.random.rand() * 4 + 1)
    counts = [int(numpy.random.rand() * 3 + 1) for i in range(inumpyuts)]
    array_list = [numpy.zeros((i, height, width)) for i in counts]
    expected_shape = tuple((sum(counts), height, width))
    return array_list, expected_shape


def test_arraystack():
    """Array stacker works"""
    t_array_list, expected_shape = makeRandomArrays()
    stacked = riomucho.utils.array_stack(t_array_list)
    assert stacked.shape == expected_shape


def test_bad_arraystack():
    """Stacking an array of wrong shape fails with ValueError"""
    t_array_list, expected_shape = makeRandomArrays()
    t_array_list.append(numpy.zeros((1, 1, 1)))
    with pytest.raises(ValueError):
        riomucho.utils.array_stack(t_array_list)


def fail(data, window, ij, g_args):
    """User functions must be defined at the top of a module."""
    return data * (1 / 0)


def test_pool_worker_traceback_capture(tmpdir, test_1_tif, test_2_tif):
    """Worker tracebacks are captured"""
    with rasterio.open(str(test_1_tif)) as src:
        options = src.profile
        options.update(count=2)

    with riomucho.RioMucho(
        [str(test_1_tif), str(test_2_tif)],
        str(tmpdir.join("output.tif")),
        fail,
        mode="array_read",
        options=options,
    ) as rm:
        with pytest.raises(riomucho.MuchoChildError) as excinfo:
            rm.run(4)

        assert "ZeroDivisionError" in str(excinfo.value)


def test_tb_capture():
    """Exception in a job is captured"""

    @riomucho.tb_capture
    def foo(*args, **kwargs):
        return 1 / 0

    with pytest.raises(riomucho.MuchoChildError) as excinfo:
        foo()
    assert "ZeroDivisionError" in str(excinfo.value)


def test_riomucho_simple_dataset_object(tmpdir, test_1_tif):
    """We can pass an open dataset for output"""
    with rasterio.open(str(test_1_tif)) as src:
        options = src.profile

    with rasterio.open(str(tmpdir.join("output.tif")), "w", **options) as dst:
        with riomucho.RioMucho([str(test_1_tif)], dst, read_function_simple) as rm:
            rm.run(1)

    with rasterio.open(str(tmpdir.join("output.tif"))) as outputsrc:
        assert numpy.sum(outputsrc.read(1)[:10, :10] != 0) == 0
