import pytest
import kodiak.config as config


class TestConfig(object):
    def test_restore_default_config(self):
        # Change 1 value
        default_unpack = config.options["unpack"]
        assert default_unpack == True
        config.options["unpack"] = False
        config.restore_default_config("unpack")
        assert config.options["unpack"] == True

        # Change more than 1 value
        default_new_col_combiner = config.options["new_col_combiner"]
        default_col_pair_combiner = config.options["col_pair_combiner"]

        config.options["new_col_combiner"] = "fake_new_col_combiner"
        config.options["col_pair_combiner"] = "fake_pair_combiner"

        config.restore_default_config("new_col_combiner", "col_pair_combiner")
        assert config.options["new_col_combiner"] == default_new_col_combiner
        assert config.options["col_pair_combiner"] == default_col_pair_combiner

        with pytest.raises(KeyError):
            config.restore_default_config("unknown_option")

    def test_base_config(self):
        default_unpack = config.base_config()['unpack']
        assert default_unpack == True

        options = config.base_config(unpack=False)
        assert options["unpack"] == False
