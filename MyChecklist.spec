# PyInstaller release configuration for the MyChecklist Windows GUI.
from pathlib import Path

project_root = Path(SPECPATH)
source_root = project_root / "src"

a = Analysis(
    [str(source_root / "mychecklist" / "__main__.py")],
    pathex=[str(source_root)],
    binaries=[],
    datas=[],
    hiddenimports=["customtkinter", "plyer"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tests"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MyChecklist",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
