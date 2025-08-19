"""WPK entry type definitions for the WPK file format."""

from dataclasses import dataclass
from enum import IntFlag, auto
import os

from core.npk.enums import (
    CompressionType,
    DecryptionType,
    NPKEntryFileCategories,
)


class WPKEntryDataFlags(IntFlag):
    """Flags for WPK entry data."""

    NONE = 0
    TEXT = auto()
    NXS3_PACKED = auto()
    ROTOR_PACKED = auto()
    ENCRYPTED = auto()
    ERROR = auto()


@dataclass
class WPKReadOptions:
    """Options for reading WPK files."""

    decryption_key: int | None = None
    aes_key: bytes | None = None
    info_size: int | None = None


@dataclass
class WPKIndex:
    """Represents an index entry in a WPK file."""

    filename: str = ""

    file_offset: int = 0
    file_length: int = 0
    file_original_length: int = 0
    zcrc: int = 0  # compressed CRC
    crc: int = 0   # decompressed CRC
    file_structure: bytes | None = None
    zip_flag: CompressionType = CompressionType.NONE
    encrypt_flag: DecryptionType = DecryptionType.NONE

    data_flags: WPKEntryDataFlags = WPKEntryDataFlags.NONE

    def __repr__(self) -> str:
        return (
            f"WPKIndex(offset=0x{self.file_offset:X}, "
            f"length={self.file_length}, "
            f"orig_length={self.file_original_length}, "
            f"compression={CompressionType.get_name(self.zip_flag)}, "
            f"encryption={DecryptionType.get_name(self.encrypt_flag)})"
        )


class WPKEntry(WPKIndex):
    """Represents a file entry in a WPK file, including the actual file data."""

    def __init__(self) -> None:
        super().__init__()
        self.data: bytes = b""
        self.extension: str = ""
        self.category: NPKEntryFileCategories = NPKEntryFileCategories.OTHER

    @property
    def is_compressed(self) -> bool:
        """Check if the entry is compressed."""
        return self.zip_flag != CompressionType.NONE

    @property
    def is_encrypted(self) -> bool:
        """Check if the entry is encrypted."""
        return self.encrypt_flag != DecryptionType.NONE

    def get_data(self) -> bytes:
        """Get the file data."""
        return self.data

    def save_to_file(self, path: str) -> None:
        """Save the file data to the specified path."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.data)

    def __repr__(self) -> str:
        return (
            f"WPKEntry(filename='{self.filename}', "
            f"length={self.file_length}, "
            f"compression={CompressionType.get_name(self.zip_flag)}, "
            f"encryption={DecryptionType.get_name(self.encrypt_flag)})"
        )
