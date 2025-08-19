"""Simple file format detection utilities.

This module provides helper functions to detect container formats
based on their header signatures. Currently supports detection of
IDX and WPK files.
"""

from __future__ import annotations

from typing import Optional

IDX_SIGNATURE = b"IDX\x00"
"""Magic bytes present at the beginning of IDX files."""

WPK_SIGNATURE = b"WPK\x00"
"""Magic bytes present at the beginning of WPK files."""

def is_idx_signature(data: bytes) -> bool:
    """Check if the given data starts with the IDX signature.

    Args:
        data: Initial bytes from a file.

    Returns:
        bool: ``True`` if the data matches the IDX signature.
    """
    return len(data) >= len(IDX_SIGNATURE) and data.startswith(IDX_SIGNATURE)

def is_wpk_signature(data: bytes) -> bool:
    """Check if the given data starts with the WPK signature.

    Args:
        data: Initial bytes from a file.

    Returns:
        bool: ``True`` if the data matches the WPK signature.
    """
    return len(data) >= len(WPK_SIGNATURE) and data.startswith(WPK_SIGNATURE)

def detect_file_type(path: str) -> Optional[str]:
    """Detect the file type of the provided path.

    Args:
        path: Path to the file to probe.

    Returns:
        The detected type (``"idx"`` or ``"wpk"``) or ``None`` if
        the file type could not be determined.
    """
    max_len = max(len(IDX_SIGNATURE), len(WPK_SIGNATURE))
    with open(path, "rb") as file:
        header = file.read(max_len)
    if is_idx_signature(header):
        return "idx"
    if is_wpk_signature(header):
        return "wpk"
    return None
