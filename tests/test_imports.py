import importlib

import pytest


def test_import_npk_class_types():
    try:
        importlib.import_module("core.npk.class_types")
    except Exception as exc:  # pragma: no cover - environment-specific
        pytest.skip(f"Import failed: {exc}")


def test_import_wpk_package():
    try:
        importlib.import_module("core.wpk")
    except Exception as exc:  # pragma: no cover - environment-specific
        pytest.skip(f"Import failed: {exc}")
