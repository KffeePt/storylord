# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['src.ui.screens', 'src.core', 'prompt_toolkit'],
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
    name='StoryLord',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StoryLord',
)

# Move output to bin/Release?
# PyInstaller outputs to dist/Name by default.
# We can use a post-build script or configure pathex, but usually simpler to let it build to dist
# and then Inno Setup picks it up.
# However, user asked for "Build into @[bin]". 
# Let's assume we manually move or config Inno to read from dist/StoryLord. 
# Or we can change the COLLECT name/path. 
# Ideally, we keep standard dist/ folder for intermediate, but let's try to output to bin/Release if possible.
# Actually, verifying setup.py logic: it calls pyinstaller story_lord.spec.
# Let's adjust Inno Setup to look in dist/StoryLord/StoryLord.exe
