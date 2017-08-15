"""Helper methods to use as colbuilders with `colgen` and `mutcol`"""


def as_attribute(x, y):
    """interprets `Match` value ``y`` as an attribute of ``x``"""
    return getattr(x, y)


def as_method(x, y):
    """interprets `Match` value ``y`` as an instance method of ``x``"""
    return getattr(x, y)()


def splitter(pattern=None):
    """A builder function that returns a `colbuilder`

    Arguments:
        pattern: a string pattern used to split a string

    Example:
        >>> from kodiak.kodiak_dataframe import KodiakDataFrame
        >>> from kodiak.colbuilders import splitter
        >>> df = KodiakDataFrame({'name': ['Groucho Marx', 'Harpo Marx']})
        >>> df.gencol('{first,last}_name', 'name', splitter(" "))

        Will return the following data frame:

        >>> #            name  first_name  last_name
        >>> # 0  Groucho Marx    Groucho      Marx
        >>> # 1    Harpo Marx      Harpo      Marx

    Returns:
        A function used as a `colbuilder`
    """
    if pattern is None:
        pattern = " "

    def func(i, x, y):
        return x.split(pattern)[i]

    return func
