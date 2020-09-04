# -*- mode: python -*-

# run the following code in CMD
# pyinstaller main.spec

block_cipher = None

a = Analysis(scripts=['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('./data', './data')],
             hiddenimports=["json",
                            "os",
                            "zipfile",
                            "urllib",
                            "xml",
                            "script.custom_widget",
                            "script.function",
                            "script.highlight",
                            "PyQt5.QtWidgets",
                            "PyQt5.QtGui",
                            "PyQt5.QtCore"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DoubleCross',
          debug=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='DoubleCross')
