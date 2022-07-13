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
dictionary form, as defined in [PEP 566](https://peps.python.org/pep-0566/#json-compatible-metadata).
The dictionary form is easier to use in a programming context. Three
functions are provided:

* `bytes_to_dict(bytes)` - convert a byte string containing metadata in the
  standard email format to dictionary format. Returns the metadata in
  dictionary form.
* `msg_to_dict(msg)` - convert an `emai.message.Message` object containing
  metadata to dictionary format. Returns the metadata in dictionary form.
* `dict_to_bytes(dict)` - convert the dictionary form back to email headers.
  Returns a byte string with the message form.

Note that the email header format specifies that metadata must be encoded
in UTF-8. The `dict_to_bytes` function enforces this by returning a UTF-8
encoded byte string. The `bytes_to_dict` function, on the other hand, will
attempt to handle input that is not encoded in UTF-8, as older metadata
writers did not enforce UTF-8. The encoding detection is relatively primitive,
and attempting to do anything with non-UTF-8 fields other than write them
back out unmodified is likely to result in mojibake.

Also, while there is a `msg_to_dict` function, there is no corresponding
`dict_to_msg` function. This is because the `email.message.Message` class
does not serialise to bytes in a form that conforms to the metadata spec,
so it is not useful to have metadata converted back to that form.

An example of using the library:

```python
metadata = pkg_metadata.bytes_to_dict(metadata_file.read_bytes())
metadata["keywords"] = ["example", "artificial"]
metadata_file.write_bytes(dict_to_bytes(metadata))
```

or, using an intermediate `Message` object:

```python
with metadata_file.open(encoding="utf-8") as f:
    msg = email.message_from_file(f)
metadata = pkg_metadata.msg_to_dict(msg)
metadata["keywords"] = ["example", "artificial"]
metadata_file.write_bytes(dict_to_bytes(metadata))
```

In addition to the metadata file format, project metadata can
also be specified in the `pyproject.toml` file, in TOML
format as specified in [PEP 621](https://peps.python.org/pep-0621/).
This library provides a function to read the `[project]` section
of `pyproject.toml` and convert it into a ("JSON format") metadata
dictionary.

* `pyproject_to_dict(pyproject)` - convert `pyproject.toml` metadata
  into a metadata dictionary. The `pyproject` argument is a dictionary
  representing the data in the `[project]` section of `pyproject.toml`.

Example:

```python
with open("pyproject.toml", "rb") as f:
    pyproject_data = tomli.load(f)

metadata = pkg_metadata.pyproject_to_dict(pyproject_data["project"])
```
