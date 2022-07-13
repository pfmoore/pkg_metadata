"""Utility classes for handling packaging metadata.
"""

__version__ = "0.3"

from .metadata import bytes_to_dict, dict_to_bytes, msg_to_dict, pyproject_to_dict

__all__ = ["bytes_to_dict", "msg_to_dict", "dict_to_bytes", "pyproject_to_dict"]
