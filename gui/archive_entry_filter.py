"""Provides a filter for archive entries in the file list."""

from core.npk.enums import NPKEntryFileCategories
from gui.utils.npk import get_npk_file, ransack_agent
from gui.utils.wpk import get_wpk_file
from gui.widgets.npk_file_list import NPKFileList
from gui.widgets.wpk_file_list import WPKFileList


class ArchiveEntryFilter:
    """Filter entries from either NPK or WPK file lists."""

    def __init__(self, list_view: NPKFileList | WPKFileList):
        self._list_view = list_view
        self.filter_string = ""
        self.filter_type: NPKEntryFileCategories | None = None
        self.include_text = True
        self.include_binary = True

        self.mesh_biped_head = False

    def apply_filter(self):
        """Filter entries based on the current settings."""
        if self._list_view.disabled():
            return

        model = self._list_view.model()
        archive_file = get_npk_file() or get_wpk_file()
        if not model or not archive_file:
            return

        for row in range(model.rowCount()):
            entry = archive_file.read_entry(row)
            filename_lower = model.get_filename(model.index(row)).lower()

            if self.include_text == self.include_binary == False:
                # If both are unchecked, hide all
                self._list_view.setRowHidden(row, True)
                continue

            text_flag = type(entry.data_flags).TEXT
            if self.include_text != self.include_binary:
                # If only one is checked, hide the other
                if self.include_text and not entry.data_flags & text_flag or (
                    self.include_binary and entry.data_flags & text_flag
                ):
                    self._list_view.setRowHidden(row, True)
                    continue

            # Text filter - quick reject
            if self.filter_string and self.filter_string not in filename_lower:
                self._list_view.setRowHidden(row, True)
                continue

            # Category filtering
            if self.filter_type is None:
                show_item = True
            elif self.filter_type == entry.category:
                if self.filter_type == NPKEntryFileCategories.MESH:
                    show_item = not self.mesh_biped_head or ransack_agent(entry.data, "biped head")
                else:
                    show_item = True
            else:
                show_item = False

            # Apply visibility
            self._list_view.setRowHidden(row, not show_item)
