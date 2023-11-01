# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['C:\\Users\\cimei\\Scripts\\SISGEDEM-PyInstaller'], 
    binaries=[],
    datas=[
        ('instance','var\\project-instance'),
        ('project\\core', 'project\\core'),
        ('project\\demandas', 'project\\demandas'),
        ('project\\error_pages', 'project\\error_pages'),
        ('project\\objetos', 'project\\objetos'),
        ('project\\static','project\\static'),
        ('project\\templates', 'project\\templates'),
        ('project\\users','project\\users')
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
