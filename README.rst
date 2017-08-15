Kodiak
======

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg

.. image:: https://readthedocs.org/projects/kodiak/badge/?version=latest
    :target: http://kodiak.readthedocs.io/en/latest/?badge=latest


Overview
--------

**Kodiak** enhances your feature engineering workflow extracting common
patterns so you can create more features faster.

Ex: You have the ``writers`` dataframe, where ``born`` is a datetime

+-----------------------+--------------+
| name                  | born         |
+=======================+==============+
| Miguel de Cervantes   | 09-29-1547   |
+-----------------------+--------------+
| William Shakespeare   | 04-23-1617   |
+-----------------------+--------------+

and you want to extract from the ``born`` column: ``day``, ``month`` and
``year`` and create 3 new columns

+-----------------------+--------------+---------------+-------------+--------------+
| name                  | born         | born\_month   | born\_day   | born\_year   |
+=======================+==============+===============+=============+==============+
| Miguel de Cervantes   | 09-29-1547   | 9             | 29          | 1547         |
+-----------------------+--------------+---------------+-------------+--------------+
| William Shakespeare   | 04-23-1617   | 4             | 23          | 1617         |
+-----------------------+--------------+---------------+-------------+--------------+

The simplest thing you could do in Pandas is:

.. code:: python

    writers["born_month"] = writers.born.map(lambda x: x.month)
    writers["born_day"]   = writers.born.map(lambda x: x.day)
    writers["born_year"]  = writers.born.map(lambda x: x.year)

With Kodiak you could get the same result in one line:

.. code:: python

    writers.gencol("born_{month,day,year}", "born", lambda x, y: getattr(x, y))
    # or more succinctly
    writers.gencol("born_{.month,.day,.year}", "born")

But, how does it work? Kodiak uses ``"born_{month,day,year}"`` as a
template for the columns: ``born_month``, ``born_day`` and ``born_year``
and passes ``month``,\ ``day`` and ``year`` as arguments to a provided
function that also has the current 'born' as an an argument, so you're
basically doing:

.. code:: python

    for y in ['month', 'day', 'year']:
        writers["born_{}".format(y)] = writers.born.map(lambda x: getattr(x, y))

Kodiak does a lot of other things to boost your workflow, for that, see
the *Basic Usage* and *Advanced Usage* sections

Installation
------------

To install Kodiak, ``cd`` to the Kodiak folder and run the install
command:

.. code:: sh

    sudo python setup.py install

You can also install Kodiak from PyPI:

.. code:: sh

    sudo pip install kodiak

Basic Usage
-----------

**Kodiak** main object is ``KodiakDataFrame`` an extension of
``pandas.Dataframe`` that provides the instance method ``colgen`` to
create one or more columns. You create ``KodiakDataFrames`` the same way
you create a ``pandas.DataFrame``

``colgen`` signature is:
``colgen(newcols, col, colbuilder=None, enum=False, config=None)``

newcols
  has a double function, it works as a specification of the columns you
  want to create, and it also contains the values passed to ``colbuilder``

  .. code:: python

      # If you want to create the columns `first_name`, `last_name`
      # and pass `first` and `last` as arguments to `colbuilder` you write
      >>> newcols = "{first,last}_name"

      # More complex patterns allowed
      >>> groups = "col_{a,b}_{c,d}"

      # Will create the columns: `col_a_c`, `col_b_d`
      # The way `a,b` and `c,d` is combined can be configured

col
  is the `KodiakDataframe` column from where you'll extract information
  to create your new column/s

colbuilder
  is a function or lambda used to extract info from ``col``
  and create the columns specified in ``newcols`` with the
  corresponding ``col`` instance and the ``newcols`` values.
  The signature of `colbuilder` is `colbuilder(x, y)` or
  `colbuilder(i, x, y)` `x` is an instance of the column passed
  in `col` and `y` is an argument extracted from `newcols`. The
  extra argument `i` is an index of the arguments.

config
  tweak Kodiak inner workings with your own config, see the
  dedicated section for more info

Advanced Usage
--------------

In this section we're going to describe the main components and concepts
that are essential to Kodiak

Templating
~~~~~~~~~~

The template language is minimal but has some extensions to help you:

Ranges
^^^^^^

The range notation is ``start:end:step``. Reverse ranges are permitted
setting ``end`` bigger than ``start``. ``step`` default value is ``1``, and
``start`` is ``0``, finally if ``end`` is absent, it'll be setted to ``0`` and
you'll have a reversed range. Ranges are inclusive.

.. code:: python

    simple_range = "col_{1:3}" # -> col_1, col_2, col_3
    step_range = "col_{:3:2}" # -> col_0, col_3
    inverse_range = "col_{3:1}" # -> col_3,col_2,col_1
    no_end = "2:" # -> col_2,col_1,col_0

Key-Value
^^^^^^^^^

If you want the column name and argument passed to the ``colbuilder`` to
differ you can use key-values.

.. code:: python

    dataframe.gencol("{short=very_long_name}_col", "col", alambda)
    # In this case the column name will be ``short_col`` but you'll pass
    # ``very_long_name`` to ``alambda``

    # key-value notation can be extended to more arguments:
    dataframe.gencol("{k1=v1,k2=v2,k3=v3}_col", "col", alambda)

.. WARNING::
  values are always interpreted as *strings* so in:
  ``col_{k=1:5}`` the value ``1:5`` is interpreted as ``"1:5"`` and not as
  a range, the same for ``col_{k=[1,2,3]}`` and any other object, also if
  you pass a number it will also be interpreted as string so you will need
  to convert it if you intend to use it as an ``int``.

Transforms
~~~~~~~~~~

Under the hood when you pass ``newcols`` to ``gencol``, Kodiak builds an
``OrderedDict`` where it's keys are column names and it's values are
tuples of ``Match`` objects -even if it's just one Match it's wrapped
inside a tuple-

.. code:: python

    newcol = "{first,last}_name"
    # will build
    args_dict = {'first_name': (Match('first'),), 'last_name': (Match('last'),)}

``Transforms`` are a way to pre-process the values and change them
enriching the ``Match`` object with a payload as you will see in the
``Default colbuilder`` section.

So, if the values are ``Match`` objects, how is that when you write your
``colbuilder`` you deal with ``strings``? Kodiak understands that if the
``Match`` object doesn't have a payload it's better to pass strings
arguments to ``colbuilder``, this behaviour can be controlled.

What's the use of ``Match`` objects and their ``payload``? What're some
examples of ``Transforms``? The next section will answer this questions

Default colbuilder
~~~~~~~~~~~~~~~~~~

As you can see in the ``colgen`` signature, ``colbuilder`` default
argument is ``None``, in special cases Kodiak can infer the
``colbuilder`` method, let's revisit the opening example.

.. code:: python

    writers.gencol("born_{.month,.day,.year}", "born")

The ``colbuilder`` in this case is inferred from the hint you gave
Kodiak in the template: ``.month``, prefixing ``month`` with a ``.``
indicates that you're referring to an attribute of ``born``, so
internally Kodiak builds a ``colbuider`` that extracts the ``month``
from a ``born`` instance. Another way of omitting the ``colbuilder`` is
when you have an instance method:

.. code:: python

    # Notice the `!` after weekday
    writers.gencol("born_{weekday!}", "born")

.. WARNING::
  This hint only works for methods with no arguments, passing
  a method with one or more arguments will raise an error

How is that Kodiak infers the ``colbuilder``? When the ``newcols`` are
processed they go through a pipeline of ``Transforms``, one of them:
``PropertyTransform`` detects that ``.month`` refers to an attribute and
enriches de ``Match`` object hinting in the payload the corresponding
``colbuilder``, that's why you don't need to pass the ``colbuilder``
argument. But what happens if you give a ``colbuilder``? In this case,
as the ``Match`` object has a ``payload`` instead of working with plain
strings you will work with tuples of ``Match`` objects

.. Note::
  Kodiak will raise an exception when it can't figure out a
  default colbuilder

Enumerations
~~~~~~~~~~~~

Sometimes you care about the position of the arguments not the exact
value, in that case you can use the ``enum`` param or the implicit
``enum`` with a function or lambda of arity 3, the first argument will
be the index starting at 0.

.. code:: python

    writers.gencol("{first=0,last=1}_name", "name", lambda x,y: x.split(" ")[int(y)])

    # Another way with enum=True
    writers.gencol("{first,last}_name", "name", lambda i,x,y: x.split(" ")[i], enum=True)

    # Without enum=True but with a colbuilder with arity 3
    writers.gencol("{first,last}_name", "name", lambda i,x,y: x.split(" ")[i])

Configuration
-------------

Almost everything is configurable in Kodiak, you could have a per-method
configuration or system-wide config.

The ``Config`` object has the following customizable params:

parser
  Kodiak by default uses the ``ArgsParser`` class to parse ``newcols``

match\_transform
  data passed to the ``colbuilder`` could be
  transformed first, by default we use the ``default_transform`` pipeline,
  you could replace it with an array of ``Transforms`` objects.

new\_col\_combiner
  in the newcols template if you have
  ``"col_{a,b}_{c,d}"``, this results in the columns: ``"col_a_c"`` and
  ``"col_b,d"``, how the different groups ``['a','b']`` and ``['c', 'd']``
  are combined is controlled with this param, currently we use the ``zip``
  function, and you could replace it with a function with similar
  signature.

unpack
  Boolean Default True, when ``newcols`` is simple, ``foo_{a,b}``
  instead of ``foo_{.a,b!}`` instead of passing to ``colbuilder``
  tuples of ``Match`` objects we just pass individual items,
  ``a``, ``b``, so it's easier to build a ``colbuilder`` without
  having to unwrap the ``Match`` tuples

col\_pair\_combiner
  Once you have the arguments that you're going to
  pass to the ``colbuilder`` you can combine them in different ways, currently
  we use ``product`` from itertools, ie: the cartesian product between an
  element, ex: ``event``, and the other n-columns, creating the following
  tuples:

  .. code:: python

      [('event', 'day') , ('event', 'month'), ('event', 'year')]

You can replace this method with another with the same signature as ``product``

Config can be accessed, modified and restored with:

.. code:: python

    >> import config
    >> from config import cfg
    >> config.options

    # Global change on config

    >> config.options["unpack"] = False
    >> config.options["col_pair_combiner"] = zip

    # Restoring one or more fields of the configuration
    >> config.restore_default_config("col_pair_combiner")

    # Restoring all the options
    >> config.restore_default_config()

    # With `base_config` or it's alias `cfg` you can create modified versions
    # of the default config

    >> dataframe.gencol("col_{a!,b!}","col", func, config=cfg(unpack=False))
