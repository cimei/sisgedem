# -*- mode: python -*-

#import sys
#sys.setrecursionlimit(5000)

block_cipher = None



a = Analysis(['app.py'],
             pathex=['C:\\Users\\cimeibt\\Documents\\PythonScripts\\SicopesPostgre'],
             binaries=[],
             datas=[
                    ('instance','var\\project-instance'),
                    ('project\\templates', 'project\\templates'),
                    ('project\\acordos', 'project\\acordos'),
                    ('project\\bolsas', 'project\\bolsas'),
                    ('project\\core', 'project\\core'),
                    ('project\\demandas', 'project\\demandas'),
                    ('project\\error_pages', 'project\\error_pages'),
                    ('project\\users','project\\users'),
                    ('project\\instrumentos', 'project\\instrumentos'),
                    ('project\\static','project\\static'),
                    ('project\\convenios', 'project\\convenios'),
                    ('project\\google_api_python_client-1.9.3.dist-info','google_api_python_client-1.9.3.dist-info'),
                    ('client.json','.'),
                    ("C:\\Users\\cimeibt\\Anaconda3\\envs\\sicopesPG\\Lib\\site-packages\\branca\\*.json","branca"),
                    ("C:\\Users\\cimeibt\\Anaconda3\\envs\\sicopesPG\\Lib\\site-packages\\branca\\templates","branca\\templates"),
                    ("C:\\Users\\cimeibt\\Anaconda3\\envs\\sicopesPG\\Lib\\site-packages\\folium\\templates","folium\\templates"),
                   ],
             hiddenimports=['google-api-python-client','sqlalchemy.sql.default_comparator'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SICOPES',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
