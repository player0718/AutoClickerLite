# -*- mode: python ; coding: utf-8 -*-
# AutoClicker 优化打包配置

block_cipher = None

# 排除不必要的模块以减小体积
excludes = [
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'PIL.ImageTk',
    'cv2',
    'unittest',
    'pydoc',
    'doctest',
    'difflib',
    'ftplib',
    'bz2',
    'lzma',
    'sqlite3',
    'asyncio',
    'concurrent',
    'multiprocessing',
    'lib2to3',
    'xmlrpc',
    'test',
]

a = Analysis(
    ['auto_clicker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤不必要的二进制文件
a.binaries = [x for x in a.binaries if not any(
    exclude in x[0].lower() for exclude in [
        'tcl86', 'tk86',  # 保留这些，tkinter需要
        'libcrypto', 'libssl',
        'qt', 'pyside', 'pyqt',
        'numpy', 'scipy',
    ]
)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 单文件模式
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标: icon='icon.ico'
)
