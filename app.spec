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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SISGEDEM',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True
)
