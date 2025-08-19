"""Provides a preview widget for Main Window."""

from typing import cast
from PySide6 import QtWidgets, QtCore

from core.npk.class_types import NPKEntry
from core.wpk.class_types import WPKEntry
from core.utils import format_bytes
from gui.utils.viewer import (
    ALL_VIEWERS,
    find_best_viewer,
    get_viewer_display_name,
    set_entry_for_viewer,
)

SELECT_ENTRY_TEXT = "Select an entry to preview."

class PreviewWidget(QtWidgets.QWidget):
    """
    A widget that provides a preview of the selected file in the NPK file list.
    """

    _current_entry: NPKEntry | WPKEntry | None = None
    _previewers: list[QtWidgets.QWidget] = []

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        self.message_label = QtWidgets.QLabel(SELECT_ENTRY_TEXT)
        self.message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.widget_layout = QtWidgets.QVBoxLayout(self)

        self.control_bar_layout = QtWidgets.QHBoxLayout()

        self.status_label = QtWidgets.QLabel()

        self.control_bar_layout.addWidget(self.status_label)

        self.control_bar_layout.addStretch()

        self.previewer_selector = QtWidgets.QComboBox(self)
        def on_previewer_selected(index: int):
            previewer = self.previewer_selector.currentData()
            if previewer is None:
                return
            self.select_previewer(previewer)
        self.previewer_selector.currentIndexChanged.connect(on_previewer_selected)

        self.control_bar_layout.addWidget(self.previewer_selector)

        self.widget_layout.addLayout(self.control_bar_layout)

        for viewer in ALL_VIEWERS:
            previewer = viewer()
            previewer.setParent(self)
            self._add_previewer(previewer)

        for previewer in self._previewers:
            previewer.setVisible(False)
            self.widget_layout.addWidget(previewer)

        self.widget_layout.addWidget(self.message_label)

        self.set_control_bar_visible(False)

    def _add_previewer(self, previewer: QtWidgets.QWidget):
        """
        Add a previewer to the preview widget.
        
        :param previewer: The previewer to add.
        :param name: The name of the previewer.
        """
        self.previewer_selector.addItem(get_viewer_display_name(previewer), previewer)
        self._previewers.append(previewer)

    def _set_data_for_previewer(
        self, previewer: QtWidgets.QWidget, data: NPKEntry | WPKEntry | None
    ):
        """
        Set the data for the previewer. When errors occur, hide the previewer and show an error message.
        
        :param previewer: The previewer to set the data for.
        :param data: The NPK entry data to set.
        """
        try:
            set_entry_for_viewer(previewer, data)
        except ValueError as e:
            previewer.setVisible(False)
            self.message_label.setText(cast(str, e.args[0]))
            self.message_label.setVisible(True)

    def set_control_bar_visible(self, visible: bool):
        """
        Set the visibility of the control bar.
        
        :param visible: Whether to show or hide the control bar.
        """
        self.status_label.setVisible(visible)
        self.previewer_selector.setVisible(visible)

    def select_previewer(self, previewer: QtWidgets.QWidget):
        """
        Select a previewer to display.
        
        :param previewer: The previewer to display.
        """
        self.message_label.setVisible(False)
        for p in self._previewers:
            # Memory cleanup
            self._set_data_for_previewer(p, None)
            p.setVisible(False)
        if self.isVisible():
            previewer.setVisible(True)

        # Set the previewer selector to the selected previewer
        self.previewer_selector.setCurrentIndex(self.previewer_selector.findData(previewer))

        if self._current_entry is None:
            return

        # Update the previewer with the current entry data
        self._set_data_for_previewer(previewer, self._current_entry)

    def set_file(self, entry: NPKEntry | WPKEntry):
        """Set the file to be previewed and select the appropriate previewer."""

        self.clear()

        self._current_entry = entry

        if hasattr(entry, "file_signature"):
            self.status_label.setText(
                f"Signature: {hex(getattr(entry, 'file_signature'))} | "
                f"Size: {format_bytes(entry.file_original_length)}"
            )
        else:
            self.status_label.setText(
                f"Size: {format_bytes(entry.file_original_length)}"
            )

        self.set_control_bar_visible(True)

        text_flag = type(entry.data_flags).TEXT
        best_previewer = find_best_viewer(entry.extension, bool(entry.data_flags & text_flag))
        for previewer in self._previewers:
            if isinstance(previewer, best_previewer):
                self.select_previewer(previewer)

    def clear(self):
        """
        Clear the preview.
        """
        for previewer in self._previewers:
            # Cleanup data in previewer to save memory
            self._set_data_for_previewer(previewer, None)
            previewer.setVisible(False)
        self.set_control_bar_visible(False)
        self.message_label.setText(SELECT_ENTRY_TEXT)
        self.message_label.setVisible(True)
        self._current_entry = None
