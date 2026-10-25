# Build on Windows: .desktop-venv\Scripts\python.exe -m PyInstaller --noconfirm DualLidarS3.spec
from pathlib import Path
from PyInstaller.utils.hooks import collect_all
root=Path(SPECPATH)
datas=[(str(root/'assets'),'assets'),(str(root/'layout.json'),'.')]
binaries=[]
hiddenimports=['viewer.dual_viewer','viewer.dual_serial','webview.platforms.edgechromium']
for package in ['viser','webview']:
    d,b,h=collect_all(package)
    datas+=d;binaries+=b;hiddenimports+=h
analysis=Analysis([str(root/'desktop.py')],pathex=[str(root)],binaries=binaries,
                  datas=datas,hiddenimports=hiddenimports,hookspath=[],hooksconfig={},
                  runtime_hooks=[],excludes=['pytest'],noarchive=False)
pyz=PYZ(analysis.pure)
exe=EXE(pyz,analysis.scripts,[],exclude_binaries=True,name='DualLidarS3',
        debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False)
coll=COLLECT(exe,analysis.binaries,analysis.datas,strip=False,upx=False,name='DualLidarS3')
