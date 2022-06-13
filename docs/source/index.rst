Reading package metadata
========================

A library of functions for reading package metadata.

Installation
------------

You can install pkg_metadata with ``pip``:

.. code-block:: console

    $ pip install pkg_metadata


Basic Usage
-----------

.. code-block:: python

    metadata = bytes_to_json(Path("METADATA").read_bytes())
    print(metadata["name"], metadata["version"])

Contents
--------

.. toctree::
   :maxdepth: 2

   pkg_metadata

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
