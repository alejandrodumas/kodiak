from __future__ import absolute_import

from kodiak.kodiak_dataframe import KodiakDataFrame
from kodiak.colbuilders import splitter

import pandas as pd

kdf = KodiakDataFrame({'name': ['Groucho Marx', 'Harpo Marx'],
                       'born': pd.to_datetime(['02-10-1890', '23-11-1888']),
                       'birthplace': ['United States,New York', 'United States,New York']})


class TestKodiakDataFrame(object):
    def test_default_colbuilder(self):
        kdf.gencol("born_{.year,.month}", "born")

        assert kdf["born_year"].values.tolist() == [1890, 1888]
        assert kdf["born_month"].values.tolist() == [2, 11]

    def test_colbuilder_basic(self):
        kdf.gencol("{first,last}_name", "name", splitter())

        assert kdf["first_name"].values.tolist() == ['Groucho', 'Harpo']
        assert kdf["last_name"].values.tolist() == ['Marx', 'Marx']

    def test_colbuilder_drop(self):
        kdf.gencol("lower_name", "name", lambda x, y: x.lower(), drop=True)

        assert kdf["lower_name"].values.tolist() == ['groucho marx', 'harpo marx']
        assert "name" not in kdf.columns

    def test_colbuilder_enum(self):
        kdf.gencol("birthplace_{country,state}", "birthplace", lambda i, x, y: x.split(",")[i], enum=True)

        assert kdf["birthplace_country"].values.tolist() == ['United States', 'United States']
        assert kdf["birthplace_state"].values.tolist() == ['New York', 'New York']
