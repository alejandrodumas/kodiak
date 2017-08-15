from __future__ import absolute_import

from collections import OrderedDict

from kodiak.config import options


class ArgsDictBuilder(object):
    def __init__(self, parser=None, transform=None, new_col_combiner=None):
        if parser is None:
            parser = options['parser']
        if transform is None:
            transform = options['match_transform']
        if new_col_combiner is None:
            new_col_combiner = options['new_col_combiner']

        self.parser = parser
        # TODO: need to be consistent with this: instance or method, decide
        self.transform = transform.transform
        self.combiner = new_col_combiner

    def build(self, new_col):
        template, group_args = self.parser.parse(new_col)

        def transform_groups(match_group):
            return [self.transform(match) for match in match_group]

        match_args = [transform_groups(group_arg) for group_arg in group_args]
        match_args = list(self.combiner(*match_args))

        # Respect key order to preserve user imposed order on columns
        args_dict = OrderedDict()
        for arg in match_args:
            match_labels = [match.label or match.value for match in arg]
            name = template.format(*match_labels)
            args_dict[name] = arg

        return args_dict
