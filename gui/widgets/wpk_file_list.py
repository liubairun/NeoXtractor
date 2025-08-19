"""Custom QListView to display WPK files."""

import os
from PySide6 import QtCore, QtWidgets

from core.wpk.class_types import WPKEntry
from gui.models.wpk_file_model import WPKFileModel
from gui.utils.wpk import get_wpk_file
from gui.utils.viewer import ALL_VIEWERS, get_viewer_display_name


class WPKFileList(QtWidgets.QListView):
    """Custom QListView to display WPK files."""

    preview_entry = QtCore.Signal(int, WPKEntry)
    open_entry = QtCore.Signal(int, WPKEntry)
    open_entry_with = QtCore.Signal(int, WPKEntry, type)

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self._disabled = False
        self._select_after_enabled: QtCore.QModelIndex | None = None

        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.doubleClicked.connect(self.on_item_double_clicked)

    def setDisabled(self, disabled: bool):  # noqa: N802 - Qt method naming
        """Set the disabled state of the list view."""
        if disabled:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.setProperty("disabled", True)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.setProperty("disabled", None)
        self.style().unpolish(self)
        self.style().polish(self)

        self._disabled = disabled

        if self._select_after_enabled:
            self.selectionModel().select(
                self._select_after_enabled,
                QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )
            self.on_current_changed(self._select_after_enabled, QtCore.QModelIndex())
            self._select_after_enabled = None

    def disabled(self) -> bool:
        """Get the disabled state of the list view."""
        return self._disabled

    def model(self) -> WPKFileModel:  # type: ignore[override]
        """Get the current model of the list view."""
        return super().model()  # type: ignore[return-value]

    def refresh_wpk_file(self) -> None:
        """Refresh the model with the current WPK file."""
        wpk_file = get_wpk_file()
        if wpk_file is None:
            self.setModel(None)
        else:
            self.setModel(WPKFileModel(wpk_file, self))
            self.selectionModel().currentChanged.connect(self.on_current_changed)

    def on_current_changed(self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex) -> None:  # noqa: ARG002
        if self._disabled:
            self._select_after_enabled = current
            return
        wpk_file = get_wpk_file()
        if not self.model() or wpk_file is None:
            return
        row_index = current.row()
        entry = wpk_file.read_entry(row_index)
        self.preview_entry.emit(row_index, entry)

    def on_item_double_clicked(self, index: QtCore.QModelIndex) -> None:
        if self._disabled:
            return
        wpk_file = get_wpk_file()
        if not self.model() or wpk_file is None:
            return
        row_index = index.row()
        entry = wpk_file.read_entry(row_index)
        self.open_entry.emit(row_index, entry)

    def show_context_menu(self, position):
        wpk_file = get_wpk_file()
        if not self.model() or wpk_file is None:
            return
        indexes = self.selectedIndexes()
        if not indexes:
            return
        menu = QtWidgets.QMenu(self)
        extract = menu.addAction("Extract")
        extract.triggered.connect(lambda: self.extract_entries(indexes))

        menu.addSeparator()
        for viewer in ALL_VIEWERS:
            viewer_action = menu.addAction("Open in " + get_viewer_display_name(viewer))
            viewer_action.triggered.connect(
                lambda _checked, v=viewer: self.open_entries_with(indexes, v)
            )
        if len(indexes) == 1:
            menu.addSeparator()
            rename = menu.addAction("Rename")
            rename.triggered.connect(lambda: self.show_rename_dialog(indexes[0]))
        menu.exec(self.viewport().mapToGlobal(position))

    def open_entries_with(self, indexes: list[QtCore.QModelIndex], viewer: type) -> None:
        wpk_file = get_wpk_file()
        if wpk_file is None:
            return
        for index in indexes:
            row = index.row()
            entry = wpk_file.read_entry(row)
            self.open_entry_with.emit(row, entry, viewer)

    def extract_entries(self, indexes: list[QtCore.QModelIndex]) -> None:
        wpk_file = get_wpk_file()
        if not self.model() or wpk_file is None:
            return
        if len(indexes) == 1:
            index = indexes[0]
            row_index = index.row()
            filename = self.model().get_filename(index)
            entry = wpk_file.read_entry(row_index)
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Extract File", filename, "All Files (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, "wb") as f:
                        f.write(entry.data)
                    QtWidgets.QMessageBox.information(
                        self, "Success", f"File extracted to {file_path}"
                    )
                except Exception as e:  # pragma: no cover - UI message
                    QtWidgets.QMessageBox.critical(
                        self, "Error", f"Failed to extract file: {str(e)}"
                    )
        else:
            dir_path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Directory to Extract Files",
                "",
                QtWidgets.QFileDialog.Option.ShowDirsOnly,
            )
            if dir_path:
                try:
                    success_count = 0
                    fail_count = 0
                    for index in indexes:
                        row_index = index.row()
                        filename = self.model().get_filename(index)
                        safe_filename = os.path.basename(filename) or f"unknown_file_{row_index}"
                        file_path = os.path.join(dir_path, safe_filename)
                        entry = wpk_file.read_entry(row_index)
                        try:
                            with open(file_path, "wb") as f:
                                f.write(entry.data)
                            success_count += 1
                        except Exception:
                            fail_count += 1
                    message = f"Extracted {success_count} files to {dir_path}"
                    if fail_count > 0:
                        message += f"\n{fail_count} files failed to extract"
                    QtWidgets.QMessageBox.information(self, "Extraction Complete", message)
                except Exception as e:  # pragma: no cover - UI message
                    QtWidgets.QMessageBox.critical(
                        self, "Error", f"Failed to extract files: {str(e)}"
                    )

    def show_rename_dialog(self, index: QtCore.QModelIndex) -> None:
        wpk_file = get_wpk_file()
        if not self.model() or wpk_file is None:
            return
        entry_index = wpk_file.indices[index.row()]
        new_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Rename File",
            f"Enter new name for {self.model().get_filename(index)}:",
            QtWidgets.QLineEdit.EchoMode.Normal,
            "",
        )
        if ok and new_name:
            entry_index.filename = new_name
            if index.row() in wpk_file.entries:
                wpk_file.entries[index.row()].filename = new_name
            model = self.model()
            model.get_filename(index, invalidate_cache=True)
            self.update(model.index(index.row()))
