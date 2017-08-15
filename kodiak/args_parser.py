import re
import itertools

DEFAULT_PATTERN = '\\{(.*?)\\}'


def _expand_range(nrange):
    """ Ranges are inclusive

    Without end is taken as a reverse range, ie.   '6:' is '6:0' infinite
    couldn't be as impossible so we think is an inverse range
    """
    bounds = nrange.split(":")
    if len(bounds) not in [2, 3]:
        raise ValueError("range must be of type begin:end or begin:end:step")

    start = bounds[0]
    end = bounds[1]

    if len(bounds) == 2:
        step = 1
    elif bounds[2] != '':
        step = bounds[2]
    else:
        # This branch cover the case "10::" and defaults to "10:0:1"
        step = 1

    if not start:
        start = "0"
    if not end:
        # As an infinite range is impossible we presuppose that's a reverse range
        end = "0"

    if not start.isdigit():
        raise ValueError("for ranges start must be a positive integer, but is: %s" % start)

    if not end.isdigit():
        raise ValueError("for ranges end must be a positive integers, but is: %s" % end)

    if int(start) > int(end):
        start, end = end, start
        expanded_range = reversed(range(int(start), int(end) + 1, int(step)))
    else:
        expanded_range = range(int(start), int(end) + 1, int(step))

    return [Match(e) for e in expanded_range]


class Match(object):
    """An object generated after the process of matching and passed to the `colbuilder`

    Attributes:
        original (str): the unmodified matched string
        value (str): a possible derived string from original
        label (str): used as the name or title of the `Match`
        payload (dict): a dict with extra information as `default_colbuilder` that can
            be used by the `colbuilder` in `kodiak_dataframe.gencol`

    """

    def __init__(self, original, label=None, value=None, payload=None):
        self.original = original
        self.value = value if value else original
        self.label = label
        self.payload = payload if payload else {}

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.original == other.original and \
                   self.value == other.value and \
                   self.label == other.label and \
                   self.payload == other.payload
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "Match(original=%r, label=%r, value=%r, payload=%r)" % (
            self.original, self.label, self.value, self.payload)


class ArgsParser(object):
    def __init__(self, pattern=None, separator=','):
        if pattern is None:
            pattern = DEFAULT_PATTERN
        self.pattern = re.compile(pattern)
        self.separator = separator

    def parse(self, string):
        args = self.pattern.findall(string)
        template = self.pattern.sub("{}", string)
        group_args = [self._parse(arg) for arg in args]

        if len(group_args) == 0:
            group_args = [[Match(None)]]

        return template, group_args

    def _parse(self, string):
        """ parses a whole group like '1,2:4' """
        args = string.split(self.separator)

        def maybe_expand(arg):
            # return _expand_range(arg) if ':' in arg else [Match(arg)]
            if '=' in arg:
                k, v = arg.split('=', 1)
                return [Match(original=arg, label=k, value=v)]
            elif ':' in arg:
                return _expand_range(arg)
            else:
                return [Match(arg)]

        args = [maybe_expand(a) for a in args]
        args = list(itertools.chain.from_iterable(args))

        return args
