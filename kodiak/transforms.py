from __future__ import absolute_import

import kodiak.colbuilders as builders


def is_number(s):
    try:
        complex(str(s))
    except ValueError:
        return False
    return True


class ComposerTransform(object):
    def __init__(self, transforms):
        """
        Arguments:
            transforms: a list of transforms
        """
        self.transforms = transforms

    def transform(self, match):
        for t in self.transforms:
            match = t.transform(match)

        return match


class PropertyTransform(object):
    def transform(self, match):
        """Adds to the `Match` object `payload` the `default_colbuilder`: `colbuilders.as_attribute`

        Args:
            match (Match): The `Match` object that is going to be enriched.

        Returns:
            Match: The enriched `Match` object with a `default_colbuilder` key in the `payload`

        Raises:
            ValueError: in case the `Match` value attribute is ambiguous.
        """
        if match.value is None:
            return match

        if is_number(match.value):
            return match

        if match.value.startswith(".") and is_number(match.value[1:]):
            raise ValueError(
                "`%s` is ambiguous because: `%s` can't be interpreted as property"
                % (match.value, match.value[1:]))

        # XXX: This doesn't catch the error ".2" Decide interpretation of ".2"
        if match.value.startswith(".") and match.value.endswith("!"):
            raise ValueError(
                "`%s` is ambiguous, name cannot start with `.` and end with `!`"
                % match.value)

        if match.value.startswith("."):
            match.value = match.value[1:]
            match.payload["default_colbuilder"] = builders.as_attribute

        return match


class MethodTransform(object):
    def transform(self, match):
        """Adds to the `Match` object `payload` the `default_colbuilder`: `colbuilders.as_method`

        Args:
            match (Match): The `Match` object that is going to be enriched.

        Returns:
            Match: The enriched `Match` object with a `default_colbuilder` key in the `payload`

        Raises:
            ValueError: in case the `Match` value attribute is ambiguous.
        """

        if match.value is None:
            return match

        if is_number(match.value):
            return match

        if match.value.endswith("!") and is_number(match.value[:-1]):
            raise ValueError(
                "`%s` is ambiguous because: `%s` can't be interpreted as method"
                % (match.value, match.value[:-1]))

        if match.value.startswith(".") and match.value.endswith("!"):
            raise ValueError(
                "`%s` is ambiguous, name cannot start with `.` and end with `!`"
                % match.value)

        if match.value.endswith("!"):
            match.value = match.value[:-1]
            # Maybe here we could catch methods whose arity is > 0
            match.payload["default_colbuilder"] = builders.as_method

        return match


class IntTransform(object):
    def transform(self, match):
        pass


default_transform = ComposerTransform([PropertyTransform(), MethodTransform()])
