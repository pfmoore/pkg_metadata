"""Utility classes for handling packaging metadata.
"""

__version__ = "0.3"

from .metadata import bytes_to_json, json_to_bytes, msg_to_json, pyproject_to_json

__all__ = ["bytes_to_json", "msg_to_json", "json_to_bytes", "pyproject_to_json"]
