#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `kodiak` package."""

import pytest

from kodiak.args_parser import ArgsParser, Match

basic_fixture = {
    "foo": ('foo', [[Match(original=None, label=None, value=None,
                           payload={})]]),
    "foo_{a,b}": ('foo_{}', [[
        Match(original='a', label=None, value='a', payload={}),
        Match(original='b', label=None, value='b', payload={})
    ]]),
    "foo_{a,b}_{c,d}": ('foo_{}_{}', [[
        Match(original='a', label=None, value='a', payload={}),
        Match(original='b', label=None, value='b', payload={})
    ], [
        Match(original='c', label=None, value='c', payload={}),
        Match(original='d', label=None, value='d', payload={})
    ]])
}

mixed_fixture = {
    "foo_{a,1:2,k=a,b=1}": ('foo_{}', [[
        Match(original='a', label=None, value='a', payload={}),
        Match(original=1, label=None, value=1, payload={}),
        Match(original=2, label=None, value=2, payload={}),
        Match(original='k=a', label='k', value='a', payload={}),
        Match(original='b=1', label='b', value='1', payload={})
    ]])
}

key_value_fixture = {
    "foo_{a=1,b=2}": ('foo_{}', [[
        Match(original='a=1', label='a', value='1', payload={}),
        Match(original='b=2', label='b', value='2', payload={})
    ]])
}

range_fixture = {
    "range_{1:3}": ('range_{}', [[
        Match(original=1, label=None, value=1, payload={}),
        Match(original=2, label=None, value=2, payload={}),
        Match(original=3, label=None, value=3, payload={})
    ]]),
    "range_{3:1}": ('range_{}', [[
        Match(original=3, label=None, value=3, payload={}),
        Match(original=2, label=None, value=2, payload={}),
        Match(original=1, label=None, value=1, payload={})
    ]]),
    "range_{1:}": ('range_{}', [[
        Match(original=1, label=None, value=1, payload={}),
        Match(original=0, label=None, value=0, payload={})
    ]]),
    "range_{:1}": ('range_{}', [[
        Match(original=0, label=None, value=0, payload={}),
        Match(original=1, label=None, value=1, payload={})
    ]]),
    "range_{1:3:2}": ('range_{}', [[
        Match(original=1, label=None, value=1, payload={}),
        Match(original=3, label=None, value=3, payload={})
    ]]),
    "range_{3:1:2}": ('range_{}', [[
        Match(original=3, label=None, value=3, payload={}),
        Match(original=1, label=None, value=1, payload={})
    ]])
}

parser = ArgsParser()


class TestArgsParser(object):
    def test_basic(self):
        for template, value in basic_fixture.items():
            assert parser.parse(template) == value

    def test_key_value(self):
        for template, value in key_value_fixture.items():
            assert parser.parse(template) == value

    def test_range(self):
        for template, value in range_fixture.items():
            assert parser.parse(template) == value

        with pytest.raises(ValueError):
            parser.parse("foo_{1:a}")
            parser.parse("foo_{a:1}")
            parser.parse("foo_{1:2:3:4}")

    def test_mixed(self):
        for template, value in mixed_fixture.items():
            assert parser.parse(template) == value
