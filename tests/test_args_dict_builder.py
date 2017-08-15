#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `kodiak` package."""

from collections import OrderedDict

import pytest

import kodiak.colbuilders as builders
from kodiak.args_dict_builder import ArgsDictBuilder
from kodiak.args_parser import Match

adb = ArgsDictBuilder()

basic_fixture = {
    "foo": OrderedDict([('foo', (Match(original=None, label=None, value=None, payload={}),))]),
    "foo_{a}": OrderedDict([('foo_a', (Match(original='a', label=None, value='a', payload={}),))]),
    "foo_{a,b}": OrderedDict([('foo_a', (Match(original='a', label=None, value='a', payload={}),)),
                              ('foo_b', (Match(original='b', label=None, value='b', payload={}),))]),
    "foo_{a,b}_{c,d}": OrderedDict([('foo_a_c',
                                     (Match(original='a', label=None, value='a', payload={}),
                                      Match(original='c', label=None, value='c', payload={}))),
                                    ('foo_b_d',
                                     (Match(original='b', label=None, value='b', payload={}),
                                      Match(original='d', label=None, value='d', payload={})))])
}

range_fixture = {
    "foo_{1:2}": OrderedDict([('foo_1', (Match(original=1, label=None, value=1, payload={}),)),
                              ('foo_2', (Match(original=2, label=None, value=2, payload={}),))]),
    "foo_{2:1}": OrderedDict([('foo_2', (Match(original=2, label=None, value=2, payload={}),)),
                              ('foo_1', (Match(original=1, label=None, value=1, payload={}),))])
}

default_colbuilder_fixture = {
    "foo_{.a}": OrderedDict([('foo_a',
                              (Match(original='.a', label=None, value='a',
                                     payload={'default_colbuilder': builders.as_attribute}),))]),
    "foo_{a!}": OrderedDict([('foo_a',
                              (Match(original='a!', label=None, value='a',
                                     payload={'default_colbuilder': builders.as_method}),))])
}

mixed_fixture = {
    "foo_{.a,b!,1:2}": OrderedDict([('foo_a',
                                     (Match(original='.a', label=None, value='a',
                                            payload={'default_colbuilder': builders.as_attribute}),)),
                                    ('foo_b',
                                     (Match(original='b!', label=None, value='b',
                                            payload={'default_colbuilder': builders.as_method}),)),
                                    ('foo_1', (Match(original=1, label=None, value=1, payload={}),)),
                                    ('foo_2', (Match(original=2, label=None, value=2, payload={}),))]),
    "foo_{.a}_{b!}": OrderedDict([('foo_a_b',
                                   (Match(original='.a', label=None, value='a',
                                          payload={'default_colbuilder': builders.as_attribute}),
                                    Match(original='b!', label=None, value='b',
                                          payload={'default_colbuilder': builders.as_method})))])
}


class TestArgsDictBuilder(object):
    def test_basic(self):
        for col, features_dict in basic_fixture.items():
            assert adb.build(col) == features_dict

        with pytest.raises(ValueError):
            adb.build("foo_{a,")

    def test_range(self):
        for col, features_dict in range_fixture.items():
            assert adb.build(col) == features_dict

    def test_default_colbuider(self):
        for col, features_dict in default_colbuilder_fixture.items():
            assert adb.build(col) == features_dict

        with pytest.raises(ValueError):
            adb.build("foo_{.a!}")
