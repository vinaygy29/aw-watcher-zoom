import platform

block_cipher = None

a = Analysis(
    ["aw_watcher_zoom/__main__.py"],
    pathex=[],
    binaries=[("aw_watcher_zoom")] if platform.system() == "Darwin" else [],
    datas=None,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="aw-watcher-zoom",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="aw-watcher-zoom",
)
