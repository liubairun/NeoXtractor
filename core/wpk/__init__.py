"""API for extracting WPK files."""

from core.npk.enums import CompressionType, DecryptionType
from core.npk.detection import get_ext

from .class_types import WPKEntry, WPKIndex, WPKReadOptions
from .wpk_file import WPKFile

__all__ = [
    "WPKFile",
    "WPKEntry",
    "WPKIndex",
    "WPKReadOptions",
    "CompressionType",
    "DecryptionType",
    "get_ext",
]
