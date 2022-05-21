"""Utility classes for handling packaging metadata.
"""

__version__ = "0.2"

from .metadata import bytes_to_json, msg_to_json, json_to_bytes, pyproject_to_json

__all__ = ["bytes_to_json", "msg_to_json", "json_to_bytes", "pyproject_to_json"]
