Converting Metadata
===================

The :py:mod:`pkg_metadata` module contains functions that convert project metadata
between the forms defined in the packaging standards - the "email header" format used
for on-disk metadata files, and the JSON-compatible dictionary format described in
:pep:`566`.

Usage
-----

.. doctest::

    >>> from pkg_metadata import bytes_to_json
    >>> metadata_bytes = b"""\
    ... Metadata-Version: 2.1
    ... Name: pkg_metadata
    ... Version: 0.3
    ... Summary: Utility classes for handling packaging metadata
    ... Author-email: Paul Moore <p.f.moore@gmail.com>
    ... Description-Content-Type: text/markdown
    ... Classifier: License :: OSI Approved :: MIT License
    ... Project-URL: Home, https://github.com/pfmoore/pkg_metadata
    ...
    ... Some description
    ... """
    >>> metadata = bytes_to_json(metadata_bytes)
    >>> metadata["name"]
    'pkg_metadata'
    >>> metadata["description"]
    'Some description\n'

Reference
---------

.. automodule:: pkg_metadata
   :members:
   :undoc-members:
   :show-inheritance:
