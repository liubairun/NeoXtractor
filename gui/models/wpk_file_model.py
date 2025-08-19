"""A custom model for displaying WPK files in a QListView."""

from typing import Any
from PySide6 import QtCore, QtWidgets

from core.wpk.class_types import WPKEntryDataFlags
from core.wpk.wpk_file import WPKFile


class WPKFileModel(QtCore.QAbstractListModel):
    """Custom model for displaying WPK files in a QListView."""

    _file_names_cache: dict[int, str] = {}

    def __init__(self, wpk_file: WPKFile, parent: QtCore.QObject | None = None):
        super().__init__(parent)

        if isinstance(parent, QtWidgets.QWidget):
            self._loading_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)
            self._encrypted_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning)
            self._errored_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical)
            self._file_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon)

        self._wpk_file = wpk_file

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex = QtCore.QModelIndex()) -> int:  # type: ignore[override]
        return len(self._wpk_file.indices)

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
             role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> Any:  # type: ignore[override]
        if not index.isValid():
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            filename = self.get_filename(index)
            if not self._wpk_file.is_entry_loaded(index.row()):
                return filename

            entry = self._wpk_file.read_entry(index.row())
            if entry.data_flags & WPKEntryDataFlags.ERROR:
                return f"{filename} (Error)"
            if entry.data_flags & WPKEntryDataFlags.ENCRYPTED:
                return f"{filename} (Encrypted)"
            return filename
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            if not self._wpk_file.is_entry_loaded(index.row()):
                return self._loading_icon

            entry = self._wpk_file.read_entry(index.row())
            if entry.data_flags & WPKEntryDataFlags.ERROR:
                return self._errored_icon
            if entry.data_flags & WPKEntryDataFlags.ENCRYPTED:
                return self._encrypted_icon
            return self._file_icon
        if role == QtCore.Qt.ItemDataRole.UserRole:
            return self._wpk_file.indices[index.row()]
        return None

    def get_filename(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, invalidate_cache: bool = False) -> str:
        """Get the filename for a given index."""
        if not index.isValid():
            return ""
        if index.row() in self._file_names_cache and not invalidate_cache:
            return self._file_names_cache[index.row()]

        filename = self._wpk_file.indices[index.row()].filename
        self._file_names_cache[index.row()] = filename
        return filename
