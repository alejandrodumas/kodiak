from __future__ import absolute_import

import inspect

from pandas import DataFrame

from kodiak.args_dict_builder import ArgsDictBuilder
from kodiak.args_parser import Match
import kodiak.config as cfg


def _unpackable(args):
    """args are unpackable if none of it's elements has a payload
    """

    def no_payload(match_group):
        return all(not match.payload for match in match_group)

    return all(no_payload(match_group) for match_group in args.values())


def _unpack(match_group):
    """Returns instead of a `Match` object only it's value, also if we have
       only one Match, return it instead of returning a list with one `Match`
    """
    unpacked = [match.value for match in match_group]
    if len(unpacked) == 1:
        unpacked = unpacked[0]

    return unpacked


def default_colbuilder(x, y):
    """ Uses `Match` payload attribute to extract a default colbuider
    """
    if not isinstance(y[0], Match):
        raise TypeError(
            "a default colbuilder can be only found when arguments are of type Match and have a `default_colbuilder`"
        )

    colbuilder = y[0].payload['default_colbuilder']

    return colbuilder(x, y[0].value)


def _func_args_arity(func):
    """ Inspect function arity: compatibility for Python 2.7 and 3
    """
    try:
        return len(inspect.signature(func).parameters)
    except AttributeError:
        return len(inspect.getargspec(func).args)


class KodiakDataFrame(DataFrame):
    """
    A KodiakDataFrame is a pandas.DataFrame that has new capabilities
    to ease your workflow: ``gencol`` and ``mutcol``

    Example:
        >>> from kodiak import KodiakDataFrame
        >>> kdf = KodiakDataFrame({'country': ['ar','br','cl','co']})
    """

    def __init__(self, *args, **kwargs):
        super(KodiakDataFrame, self).__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return KodiakDataFrame

    def gencol(self,
               newcols,
               col,
               colbuilder=None,
               drop=None,
               enum=False,
               config=None):
        """Generate new columns following the `newcols` pattern based on `col`

        Args:
            newcols (str) : new column/s template string
            col (str) : column name from where data is taken
            colbuilder: a function to build the new columns, could be omitted if
                it can be deduced from newcols. Usually the signature of the
                function has two arguments x, y, x is the data extracted from
                `col` and `y` is the argument extracted from the ``newcols``
                template.

                Example:
                    If `newcol` is ``"born_{month,day,year}"``, ``col`` is ``born``
                    and an instance of ``born`` is the date ``1980-12-24``, then
                    in different instances ``x``, ``y`` would be
                    ``('1980-12-24', 'month')``
                    ``('1980-12-24','day')``
                    ``('1980-12-24','year')``
            drop (bool): True if you want to drop the column `col`
            enum (bool): False by default. If true, it expects that the signature
                of the ``colbuilder`` has three arguments: ``index``, ``x`` and ``y``
            config: custom configuration build with `base_config`

        Raises:
            ValueError
        """
        if config is None:
            config = cfg.options

        if colbuilder is None and enum:
            raise ValueError(
                "Default Colbuilder is unsupported for enum = True")

        if colbuilder is None:
            colbuilder = default_colbuilder

        if drop is None:
            drop = config['drop']

        args_builder = ArgsDictBuilder(config['parser'],
                                       config['match_transform'],
                                       config['new_col_combiner'])

        args = args_builder.build(newcols)

        return self._gencol(args, col, colbuilder, drop, enum, config)

    def _gencol(self, args, col, colbuilder, drop, enum, config):
        combiner = config['col_pair_combiner']

        if config['unpack'] and _unpackable(args):
            args = {k: _unpack(match_group) for k, match_group in args.items()}

        col_args = combiner([col], args.items())

        if enum or _func_args_arity(colbuilder) == 3:
            col_args = enumerate(col_args)
            for idx, (oldcol, (newcol, val)) in col_args:
                self[newcol] = self[oldcol].map(
                    lambda x: colbuilder(idx, x, val))
        else:
            for oldcol, (newcol, val) in col_args:
                self[newcol] = self[oldcol].map(lambda x: colbuilder(x, val))

        if drop:
            self.drop(col, axis=1, inplace=True)

        return self

    def mutcol(self, col, colbuilder=None, config=None):
        """ Mutates the column `col`. Similar to gencol with newcols and col equals to `col`
        """
        return self.gencol(
            col,
            col,
            colbuilder=colbuilder,
            drop=False,
            enum=False,
            config=config)
