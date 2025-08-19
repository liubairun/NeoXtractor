"""WPK File Reader"""

import io
import os
from typing import List, Dict

from core.binary_readers import read_uint32, read_uint16
from core.npk.decompression import (
    check_nxs3,
    decompress_entry,
    unpack_nxs3,
    check_rotor,
    unpack_rotor,
)
from core.npk.decryption import decrypt_entry
from core.npk.detection import get_ext, get_file_category, is_binary
from core.logger import get_logger

from .class_types import (
    WPKEntryDataFlags,
    WPKIndex,
    WPKEntry,
    WPKReadOptions,
    CompressionType,
    DecryptionType,
)


class WPKFile:
    """Main class for handling WPK files."""

    def __init__(
        self,
        idx_path: str,
        wpk_path: str | None = None,
        options: WPKReadOptions | None = None,
    ):
        """Initialize the WPK file handler."""
        self.idx_path = idx_path
        self.wpk_path = wpk_path or os.path.splitext(idx_path)[0] + ".wpk"
        self.options = options or WPKReadOptions()

        self.entries: Dict[int, WPKEntry] = {}
        self.indices: List[WPKIndex] = []

        get_logger().info("Opening WPK index: %s", self.idx_path)

        with open(self.idx_path, "rb") as f:
            self._read_indices(f)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def _read_indices(self, idx_file: io.BufferedReader) -> None:
        """Read index entries from the IDX file."""
        count = read_uint32(idx_file)
        for _ in range(count):
            index = WPKIndex()
            index.file_offset = read_uint32(idx_file)
            index.file_length = read_uint32(idx_file)
            index.file_original_length = read_uint32(idx_file)
            index.zip_flag = CompressionType(read_uint16(idx_file))
            index.encrypt_flag = DecryptionType(read_uint16(idx_file))
            name_len = read_uint16(idx_file)
            index.filename = idx_file.read(name_len).decode("utf-8")
            self.indices.append(index)
            get_logger().debug("Index: %s", index)

    def is_entry_loaded(self, index: int) -> bool:
        """Check if an entry is already loaded."""
        return index in self.entries

    def read_entry(self, index: int) -> WPKEntry:
        """Get an entry by its index."""
        if index in self.entries:
            return self.entries[index]

        entry = WPKEntry()
        if not 0 <= index < len(self.indices):
            get_logger().critical("Entry index out of range: %d", index)
            entry.data_flags |= WPKEntryDataFlags.ERROR
            return entry

        idx = self.indices[index]
        for attr in vars(idx):
            setattr(entry, attr, getattr(idx, attr))

        with open(self.wpk_path, "rb") as file:
            self._load_entry_data(entry, file)

        if entry.extension:
            entry.filename = f"{entry.filename}.{entry.extension}"

        self.entries[index] = entry
        return entry

    def _load_entry_data(self, entry: WPKEntry, file: io.BufferedReader) -> None:
        """Load the data for an entry from the WPK file."""
        file.seek(entry.file_offset)
        entry.data = file.read(entry.file_length)

        if entry.encrypt_flag != DecryptionType.NONE:
            entry.data = decrypt_entry(entry, self.options.decryption_key)

        if entry.zip_flag != CompressionType.NONE:
            try:
                entry.data = decompress_entry(entry)
            except Exception:
                if self.options.decryption_key is not None and self.options.decryption_key != 0:
                    get_logger().error("Error decompressing file; check decryption key")
                    entry.data_flags |= WPKEntryDataFlags.ENCRYPTED
                else:
                    get_logger().critical(
                        "Error decompressing the file using %s compression",
                        CompressionType.get_name(entry.zip_flag),
                    )
                    entry.data_flags |= WPKEntryDataFlags.ERROR
                return

        if check_rotor(entry):
            entry.data_flags |= WPKEntryDataFlags.ROTOR_PACKED
            entry.data = unpack_rotor(entry.data)

        if check_nxs3(entry):
            entry.data_flags |= WPKEntryDataFlags.NXS3_PACKED
            entry.data = unpack_nxs3(entry.data)

        if not is_binary(entry.data):
            entry.data_flags |= WPKEntryDataFlags.TEXT

        entry.extension = get_ext(entry.data, entry.data_flags)
        entry.category = get_file_category(entry.extension)
        get_logger().debug("Entry %s: %s", entry.filename, entry.category)

    def extract_all(self, output_dir: str) -> None:
        """Extract all entries to the specified directory."""
        for i in range(len(self.indices)):
            entry = self.read_entry(i)
            path = os.path.join(output_dir, entry.filename)
            entry.save_to_file(path)
