# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Path to Qt plugins (update this path accordingly)
qt_plugins_path = "/Users/samalexies/venv/lib/python3.13/site-packages/PyQt6/Qt6/plugins"

# Project root (where main.py is located)
project_root = os.path.abspath(".")

# Function to collect files recursively
def get_data_files(source_dir, target_dir):
    data_files = []
    for dirpath, _, filenames in os.walk(source_dir):
        if filenames:
            dest = os.path.join(target_dir, os.path.relpath(dirpath, source_dir))
            src_files = [(os.path.join(dirpath, f), dest) for f in filenames]
            data_files.extend(src_files)
    return data_files

# List of files to bundle
added_files = []

# Add directories recursively
added_files += get_data_files('ui', 'ui')
added_files += get_data_files('asset', 'asset')

# Add config files directly
added_files.append(('database/config.json', 'database'))
added_files.append(('credentials.json', '.'))

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=added_files + [
        # Include Qt platform plugins for macOS GUI support
        (os.path.join(qt_plugins_path, 'platforms'), 'qt/plugins/platforms'),
    ],
    hiddenimports=[
        'PyQt6',
        'psycopg2',
        'json',
        'traceback',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PapersyncApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for terminal output
    disable_windowed_traceback=False,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='PapersyncApp',
)