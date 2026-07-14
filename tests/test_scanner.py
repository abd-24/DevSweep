"""
tests/test_scanner.py

Tests for recursive directory traversal in scanner.py.
"""
import sys
from pathlib import Path
import pytest
from scanner.scanner import scan, ALWAYS_SKIP
from scanner.detector import ALL_DELETABLES

def test_scan_finds_folders(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    
    result = scan(tmp_path)
    assert tmp_path / "src" in result.folders

def test_scan_finds_files(tmp_path):
    file_path = tmp_path / "main.py"
    file_path.write_text("print('hello')")

    result = scan(tmp_path)
    assert file_path in result.files

def test_scan_skips_always_skip(tmp_path):
    (tmp_path / ".git").mkdir()

    result = scan(tmp_path)
    assert tmp_path / ".git" not in result.folders


def test_scan_skips_deletables(tmp_path):
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "pyvenv.cfg").write_text("")
    result = scan(tmp_path, skip_deletables=ALL_DELETABLES)
    assert tmp_path / "venv" / "pyvenv.cfg" not in result.files

def test_scan_records_deletables(tmp_path):
    (tmp_path / "venv").mkdir()

    result = scan(tmp_path, skip_deletables=ALL_DELETABLES)
    assert tmp_path / "venv" in result.folders

@pytest.mark.skipif(sys.platform == "win32", reason="symlinks require admin on Windows")
def test_scan_skips_symlinks(tmp_path):
    (tmp_path / "real_folder").mkdir()
    symlink_path = tmp_path / "symlink_folder"
    symlink_path.symlink_to(tmp_path / "real_folder", target_is_directory=True)
    result = scan(tmp_path)

    assert symlink_path not in result.folders


def test_scan_skips_hidden_files(tmp_path):
    (tmp_path / ".env").write_text("SECRET_KEY=12345")
    result = scan(tmp_path, skip_hidden=True)

    assert tmp_path / ".env" not in result.files
