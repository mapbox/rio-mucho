"""TODO
"""

from __future__ import with_statement
from functools import wraps
from multiprocessing import Pool
import sys
import traceback

import rasterio
from rasterio.transform import guard_transform

from riomucho import utils
from riomucho.single_process_pool import MockTub


global_args = None
srcs = None


class MuchoChildError(Exception):
    """A wrapper for exceptions in a child process.

    See https://bugs.python.org/issue13831
    """

    def __init__(self):
        """Wrap the last exception."""
        exc_type, exc_value, exc_tb = sys.exc_info()
        self.exception = exc_value
        self.formatted = "".join(
            traceback.format_exception(exc_type, exc_value, exc_tb)
        )

    def __str__(self):
        return "{}\nChild process's traceback:\n{}".format(
            Exception.__str__(self), self.formatted
        )


def tb_capture(func):
    """A decorator which captures worker tracebacks.

    Tracebacks in particular, are captured. Inspired by an example in
    https://bugs.python.org/issue13831.

    This decorator wraps rio-mucho worker tasks.

    Parameters
    ----------
    func : function
        A function to be decorated.

    Returns
    -------
    func

    """

    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)

        except Exception:
            raise MuchoChildError()

    return wrapper


def init_worker(inpaths, g_args):
    """The multiprocessing worker initializer

    Parameters
    ----------
    inpaths : list of str
        A list of dataset paths.
    g_args : dict
        Global arguments.

    Returns
    -------
    None

    """
    global global_args
    global srcs
    global_args = g_args
    srcs = [rasterio.open(i) for i in inpaths]


class ReaderBase(object):
    """Base class for readers"""

    def __init__(self, user_func):
        """Create new instance

        Parameters
        ----------
        user_func : function
            The user function with signature (data, window, ij, global_args)

        Returns
        -------
        ReaderBase

        """
        self.user_func = user_func


class manual_reader(ReaderBase):
    """Warps the user's func in a manual reading pattern.
    """

    @tb_capture
    def __call__(self, args):
        """Execute the user function."""
        window, ij = args
        return self.user_func(srcs, window, ij, global_args), window


class array_reader(ReaderBase):
    """Wraps the user's func in an array reading pattern.
    """

    @tb_capture
    def __call__(self, args):
        """Execute the user function."""
        window, ij = args
        return (
            self.user_func(
                utils.array_stack([src.read(window=window) for src in srcs]),
                window,
                ij,
                global_args,
            ),
            window,
        )


class simple_reader(ReaderBase):
    """Wraps the user's func in a simple reading pattern.
    """

    @tb_capture
    def __call__(self, args):
        """Execute the user function."""
        window, ij = args
        return (
            self.user_func(
                [src.read(window=window) for src in srcs], window, ij, global_args
            ),
            window,
        )


class RioMucho(object):
    """Maps a raster processing function over blocks of data.

    Uses a multiprocessing pool to distribute the work.
    """

    def __init__(
        self,
        inpaths,
        outpath_or_dataset,
        run_function,
        mode="simple_read",
        windows=None,
        options=None,
        global_args=None,
    ):
        """Create a new instance

        Parameters
        ----------
        inpaths : list of str
            A list of input dataset paths or identifiers.
        outpath_or_dataset: str or dataset opened in 'w' mode
            This parameter specifies the dataset to which results will be
            written. If a str, a new dataset object will be created. Otherwise
            the results will be written to the open dataset.
        run_function : function
            The function to be mapped.
        mode : str, optional
            One of ["simple_read", "manual_read", "array_read"].
        windows : list, optional
            A list of windows to work on. If not overridden, this will be the
            block windows of the first source dataset.
        options : dict
            Creation options for the output dataset. If not overridden, this
            will be the profile of the first source dataset.
        global_args : dict
            Extra arguments for the user function.

        Returns
        -------
        RioMucho

        """
        self.inpaths = inpaths
        self.outpath_or_dataset = outpath_or_dataset
        self.run_function = run_function

        if mode not in ["simple_read", "manual_read", "array_read"]:
            raise ValueError(
                'mode must be one of: ["simple_read", "manual_read", "array_read"]'
            )

        else:
            self.mode = mode

        self.windows = windows or utils.getWindows(inpaths[0])
        self.options = options or utils.getOptions(inpaths[0])
        self.global_args = global_args or {}

    def __enter__(self):
        return self

    def __exit__(self, ext_t, ext_v, trace):
        pass

    def run(self, processes=4):
        """TODO"""
        if processes == 1:
            self.pool = MockTub(init_worker, (self.inpaths, self.global_args))
        else:
            self.pool = Pool(processes, init_worker, (self.inpaths, self.global_args))

        self.options["transform"] = guard_transform(self.options["transform"])

        if self.mode == "manual_read":
            reader_worker = manual_reader(self.run_function)
        elif self.mode == "array_read":
            reader_worker = array_reader(self.run_function)
        else:
            reader_worker = simple_reader(self.run_function)

        if isinstance(self.outpath_or_dataset, rasterio.io.DatasetWriter):
            destination = self.outpath_or_dataset
        else:
            destination = rasterio.open(self.outpath_or_dataset, "w", **self.options)

        # Open an output file, work through the function in parallel,
        # and write out the data.
        with destination as dst:
            for data, window in self.pool.imap_unordered(reader_worker, self.windows):
                dst.write(data, window=window)

        self.pool.close()
        self.pool.join()
