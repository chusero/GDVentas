# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['C:\\xampp\\htdocs\\software venta'],
    binaries=[],
    
    datas=[
    ('C:\\xampp\\htdocs\\software venta\\*.json', '.'),
    ('C:\\xampp\\htdocs\\software venta\\*.py', '.'),
    ('C:\\xampp\\htdocs\\software venta\\*.png', '.'),
    ('C:\\xampp\\htdocs\\software venta\\*.jpg', '.'),

    ],
    hiddenimports=['tkcalendar','tkinter','babel.numbers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    target_architecture="x86" 
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GD_Ventas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GD_Ventas2',
)