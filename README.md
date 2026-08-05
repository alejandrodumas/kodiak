

# kodiak

A library to enhance your feature engineering workflow with Pandas.

`kodiak` extends `pandas.DataFrame` to provide convenient methods for generating and mutating columns using intuitive template strings.

## Installation

```bash
pip install kodiak
```

*Requires Python 2.6, 2.7, 3.3, 3.4, or 3.5 and `pandas`.*

## Usage

Import `KodiakDataFrame` and use it like a standard Pandas DataFrame:

```python
from kodiak import KodiakDataFrame
import pandas as pd

df = KodiakDataFrame({
    'name': ['Groucho Marx', 'Harpo Marx'],
    'born': pd.to_datetime(['02-10-1890', '23-11-1888']),
    'birthplace': ['United States,New York', 'United States,New York']
})
```

### Generating Columns with `gencol`

The `gencol(newcols, col, colbuilder=None, drop=False)` method generates new columns based on a template string and a source column.

**Template Syntax**
Use curly braces `{}` to define groups of values that will be iterated over to create new column names and arguments:
- `"foo_{a,b}"` -> generates `foo_a`, `foo_b`
- `"foo_{1:3}"` -> generates `foo_1`, `foo_2`, `foo_3` (ranges are inclusive)
- `"foo_{.attr}"` -> automatically uses attribute access on the source column values
- `"foo_{method!}"` -> automatically calls the method on the source column values
- `"foo_{key=value}"` -> passes named arguments

**Examples**

Generate date components without writing a custom builder:
```python
# Automatically extracts .year and .month from datetime objects
df.gencol("born_{.year,.month}", "born")
# Creates columns: 'born_year', 'born_month'
```

Split strings using a custom builder:
```python
from kodiak.colbuilders import splitter

# Splits the 'name' column by space and creates first_name and last_name
df.gencol("{first,last}_name", "name", splitter(" "))
# Creates columns: 'first_name', 'last_name'
```

Pass an index to the builder using `enum=True`:
```python
# Splits by comma and assigns index 0 to country, 1 to state
df.gencol("birthplace_{country,state}", "birthplace",
          lambda i, x, y: x.split(",")[i], enum=True)
# Creates columns: 'birthplace_country', 'birthplace_state'
```

Drop the original column after generation:
```python
df.gencol("lower_name", "name", lambda x, y: x.lower(), drop=True)
```

### Mutating Columns with `mutcol`

The `mutcol(col, colbuilder=None)` method applies a transformation directly to an existing column in-place.

```python
df.mutcol("name", lambda x, y: x.upper())
```

## Configuration

`kodiak` uses a global configuration object that can be customized to change parsing, combining, or unpacking behaviors. You can adjust it using `kodiak.config.cfg()`.

```python
import kodiak.config as cfg

# Create a custom config
custom_cfg = cfg(unpack=False)

df.gencol("example_{a,b}", "source", config=custom_cfg)
```

To restore the default configuration at any time:
```python
cfg.restore_default_config()
```

## Testing

`kodiak` uses `pytest` and `tox` for testing across multiple Python versions.

```bash
pip install tox
tox
```

## License

MIT License. Copyright (c) 2017 Ezequiel Erbaro.
