# Manage Package Metadata

**Warning**: This project is very early alpha release, so all APIs
could change with little or no notice.

Python packages have metadata describing information like the package
name, version, etc. The details of this metadata are defined in
[the Packaging User Guide](https://packaging.python.org/en/latest/specifications/core-metadata/).
When stored in a file (either on the filesystem, or in a package
distribution) the metadata is saved in a format which is based on email
headers.

This library transforms that metadata to and from a JSON-compatible
form, as defined in [PEP 566](https://peps.python.org/pep-0566/#json-compatible-metadata).
The JSON form is easier to use in a programming context. Two functions
are provided:

* `msg_to_json(msg)` - convert the email header format to JSON.
  The `msg` argument is the metadata in email format, as an
  `email.message.Message` object. Returns a dictionary following
  the layout in the "json" form.
* `json_to_msg(json)` - convert the JSON form back to email headers.
  The `json` argument is a dictionary following the "json" form.
  Returns a (Unicode) string with the message form.

Note the discrepancy between the two `msg` forms: a `Message` object
and a string. This is something that may change, as it's a bit of
an awkward discrepancy, but there are reasons for this approach:

1. When reading metadata, the file is supposed to be in the UTF-8
   encoding, but historically this has not always been the case.
   By using a `Message` as the input, this can be constructed from
   either text or bytes (`message_from_string` or `message_from_bytes`)
   which allows the email package to handle encoding issues. If a
   project uses non-UTF8 metadata, it's likely that this approach will
   result in mojibake, but at least the data will be usable.
2. When writing metadata, using a `Message` object results in unwanted
   header fields, because the object assumes this is a "real" email,
   and not just data re-using that format. So it is more reliable
   to simply return the output in string format. It can then be written
   to a file (in UTF-8) as required.

An example of using the library:

```python
with open(metadata_file, "r", encoding="utf-8") as f:
    msg = email.message_from_file(f)
metadata = pkg_metadata.msg_to_json(msg)
metadata["keywords"] = ["example", "artificial"]
with open(metadata_file, "w", encoding="utf-8") as f:
    f.write(json_to_msg(metadata))
```

In addition to the metadata file format, project metadata can
also be specified in the `pyproject.toml` file, in TOML
format as specified in [PEP 621](https://peps.python.org/pep-0621/).
This library provides a function to read the `[project]` section
of `pyproject.toml` and convert it into a ("JSON format") metadata
dictionary.

* `pyproject_to_json(pyproject)` - convert `pyproject.toml` metadata
  into a metadata dictionary. The `pyproject` argument is a dictionary
  representing the data in the `[project]` section of `pyproject.toml`.

Example:

```python
with open("pyproject.toml", "rb") as f:
    pyproject_data = tomli.load(f)

metadata = pkg_metadata.pyproject_to_json(pyproject_data["project"])
```
