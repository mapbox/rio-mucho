class MockTub:
    """
    Class to mock multiprocessing.Pool
    """
    def __init__(self, main_worker, args):
        main_worker(*args)
    def imap_unordered(self, reader_worker, iterable):
        for i in iterable:
            yield reader_worker(i)
    def close(self):
        pass
    def join(self):
        pass