from __future__ import absolute_import

from itertools import product

from kodiak.args_parser import ArgsParser
from kodiak.transforms import default_transform


def base_config(parser=None,
                match_transform=None,
                new_col_combiner=None,
                unpack=None,
                drop=None,
                col_pair_combiner=None):
    """Default config used by `gencol` and `mutcol`

    Args:
        parser: Kodiak by default uses `ArgsParser` to parse `newcols`
        match_transform: data passed to the `colbuilder` could be transformed first,
            by default we use the `default_transform` pipeline, you could replace it
            with an array of `Transforms` objects.
        new_col_combiner: params present in the `newcols` template provide arguments
            to the `colbuilder` you can combine arguments in different groups in
            different ways, ie: "foo_{a,b}_{c,d}" has two groups: ['a','b'] and
            ['c', 'd'] by default we use `zip` but you could replace it with a
            function with equal signature.
        unpack (bool): True by default. The arguments passed to the `colbuilder` is
            of type `Match` in certain occasions you can pass strings
        drop (bool): False by default. Set to True if you want to drop the
            column `col` in `gencol` after the new columns are created
        col_pair_combiner: Once you have the arguments from the newcol template string
            they're combined with the data extracted from the `col`. This option
            controls the way this two elements are combined. Currently we use
            `product` from `itertools`, any replacement must fulfill the same
            signature.


    Returns:
        dict with base config options
    """
    base_cfg = dict(
        unpack=True,
        drop=False,
        match_transform=default_transform,
        new_col_combiner=zip,
        col_pair_combiner=product,
        parser=ArgsParser())

    if parser is not None:
        base_cfg['parser'] = parser
    if match_transform is not None:
        base_cfg['match_transform'] = match_transform
    if new_col_combiner is not None:
        base_cfg['new_col_combiner'] = new_col_combiner
    if unpack is not None:
        base_cfg['unpack'] = unpack
    if col_pair_combiner is not None:
        base_cfg['col_pair_combiner'] = col_pair_combiner

    return base_cfg


# alias introduced to ease custom configuration on gencol and mutcol
#
# ex: df.gencol("event_{.day,.month,.year}", "event", config=cfg(unpack=False))
cfg = base_config

options = base_config()


def restore_default_config(*keys):
    """Restore original configuration on all or specific properties

    If no key is present the whole configuration will be restored, if
    keys are present only them will be restored

    Args:
        keys: a list of strings that correspond to options

    Returns:
        Nothing

    Raises:
        KeyError if key is not a valid option
    """
    global options
    base_cfg = base_config()

    if len(keys) == 0:
        options = base_config()
        return

    for key in keys:
        options[key] = base_cfg[key]
