"""WPK file utility functions."""

from typing import cast

from PySide6 import QtCore

from core.wpk.wpk_file import WPKFile

def get_wpk_file() -> WPKFile | None:
    """Get the current WPK file from the application instance."""
    return cast(QtCore.QCoreApplication, QtCore.QCoreApplication.instance()).property("wpk_file")
