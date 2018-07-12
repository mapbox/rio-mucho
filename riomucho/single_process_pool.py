"""Multiprocessing Pool test double"""


class MockTub(object):
    """Class to mock multiprocessing.Pool
    """

    def __init__(self, main_worker, args):
        """Create a new instance"""
        main_worker(*args)

    def imap_unordered(self, func, iterable):
        """Map the func over the iterable"""
        for item in iterable:
            yield func(item)

    def close(self):
        """The pool is closed"""
        pass

    def join(self):
        """Everybody out of the pool"""
        pass
