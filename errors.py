class NoLabelsError(ValueError):
    """
    This is exceptions, which can be raised if no dict with labels or empty dict have been provided.
    """
    pass


class NotSortedError(ValueError):
    """
    This is exception, which can be raised if items of some data structure are not sorted.
    """
    pass
