# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ramain/resources/icons', 'ramain/resources/icons'), ('ramain/resources/themes', 'ramain/resources/themes'), ('ramain/resources/fonts', 'ramain/resources/fonts'), ('RamAIn.ico', '.')],
    hiddenimports=['sklearn.neighbors._partition_nodes', 'matplotlib.backends.backend_ps', 'matplotlib.backends.backend_svg', 'matplotlib.backends.backend_pdf'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RamAIn',
    icon='RamAIn.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RamAIn',
)
