# -*- mode: python -*-

# if you use pyqt5, this patch must be adjusted
# https://github.com/bjones1/pyinstaller/tree/pyqt5_fix

block_cipher = None

a = Analysis(scripts=['main.py'],
             pathex=['C:\\Users\\Jeuk Hwang\\PycharmProjects\\DoubleCross10'],
             binaries=[],
             datas=[('./data', './data'),
                    ('./script', './script')],
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
