# -*- mode: python ; coding: utf-8 -*-
"""
CAJanus PyInstaller构建配置文件
用于生成跨平台的可执行文件
"""

import sys
import os
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent
src_path = project_root / "src"

# 添加源码路径
sys.path.insert(0, str(src_path))

# 数据文件和资源
datas = [
    # 配置文件
    ('config', 'config'),
    # 资源文件
    ('resources', 'resources'),
    # 文档文件
    ('docs', 'docs'),
    # 许可证文件
    ('LICENSE', '.'),
    ('README.md', '.'),
]

# 隐藏导入（PyInstaller可能无法自动检测的模块）
hiddenimports = [
    # PyQt5相关
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.QtTest',
    
    # 系统监控
    'psutil',
    'psutil._psutil_windows',  # Windows特定
    'psutil._psutil_osx',      # macOS特定
    'psutil._psutil_linux',    # Linux特定
    
    # 配置和数据处理
    'yaml',
    'json',
    'pickle',
    'sqlite3',
    
    # 网络和系统
    'socket',
    'subprocess',
    'threading',
    'multiprocessing',
    
    # 平台特定模块
    'platform',
    'os',
    'sys',
    'pathlib',
    
    # 加密和安全
    'cryptography',
    'cryptography.fernet',
    'hashlib',
    
    # 日期时间
    'datetime',
    'time',
    'dateutil',
    
    # 正则表达式
    're',
    
    # 数学和统计
    'math',
    'statistics',
    
    # Windows特定
    'winreg',
    'wmi',
    'win32api',
    'win32con',
    'win32security',
    
    # macOS特定
    'objc',
    'Foundation',
    'AppKit',
    
    # Linux特定
    'dbus',
]

# 排除的模块（减少打包大小）
excludes = [
    # 开发工具
    'pytest',
    'pylint',
    'black',
    'flake8',
    'mypy',
    
    # 文档工具
    'sphinx',
    'docutils',
    
    # 测试框架
    'unittest',
    'nose',
    
    # 不需要的GUI工具包
    'tkinter',
    'wx',
    'gtk',
    
    # 不需要的科学计算库
    'numpy',
    'scipy',
    'matplotlib',
    'pandas',
    
    # 不需要的网络库
    'tornado',
    'flask',
    'django',
    
    # 其他不需要的库
    'IPython',
    'jupyter',
]

# 分析配置
a = Analysis(
    ['gui_main.py'],  # 入口脚本
    pathex=[str(src_path)],  # 搜索路径
    binaries=[],  # 二进制文件
    datas=datas,  # 数据文件
    hiddenimports=hiddenimports,  # 隐藏导入
    hookspath=[],  # 钩子路径
    hooksconfig={},  # 钩子配置
    runtime_hooks=[],  # 运行时钩子
    excludes=excludes,  # 排除模块
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,  # 加密密钥
    noarchive=False,
)

# PYZ配置（Python字节码归档）
pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=None
)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CAJanus',  # 可执行文件名
    debug=False,  # 调试模式
    bootloader_ignore_signals=False,
    strip=False,  # 去除符号
    upx=True,  # UPX压缩
    upx_exclude=[],  # UPX排除文件
    runtime_tmpdir=None,
    console=False,  # 控制台模式
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 图标文件（根据平台选择）
    icon='resources/icons/app.ico' if sys.platform == 'win32' else 
         'resources/icons/app.icns' if sys.platform == 'darwin' else
         'resources/icons/app.png'
)

# macOS应用程序包配置
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='CAJanus.app',
        icon='resources/icons/app.icns',
        bundle_identifier='com.example.cajanus',
        info_plist={
            'CFBundleName': 'CAJanus',
            'CFBundleDisplayName': 'CAJanus - 设备指纹识别与修改工具',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleIdentifier': 'com.example.cajanus',
            'CFBundleExecutable': 'CAJanus',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'CJNS',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSMinimumSystemVersion': '10.14.0',
            'NSHumanReadableCopyright': 'Copyright © 2024 CAJanus Project. Educational use only.',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'CAJanus Backup File',
                    'CFBundleTypeExtensions': ['cjbak'],
                    'CFBundleTypeRole': 'Editor',
                    'CFBundleTypeIconFile': 'backup.icns'
                }
            ]
        }
    )

# 构建后处理
def post_build():
    """构建后处理函数"""
    import shutil
    
    # 复制额外文件
    dist_dir = Path('dist')
    
    if sys.platform == 'win32':
        # Windows特定处理
        exe_dir = dist_dir / 'CAJanus'
        if exe_dir.exists():
            # 复制Visual C++运行时（如果需要）
            pass
    
    elif sys.platform == 'darwin':
        # macOS特定处理
        app_dir = dist_dir / 'CAJanus.app'
        if app_dir.exists():
            # 设置应用程序权限
            os.chmod(app_dir / 'Contents' / 'MacOS' / 'CAJanus', 0o755)
    
    elif sys.platform.startswith('linux'):
        # Linux特定处理
        exe_path = dist_dir / 'CAJanus'
        if exe_path.exists():
            # 设置可执行权限
            os.chmod(exe_path, 0o755)
            
            # 创建AppImage目录结构（可选）
            appdir = dist_dir / 'CAJanus.AppDir'
            if not appdir.exists():
                appdir.mkdir()
                
                # 复制可执行文件
                shutil.copy2(exe_path, appdir / 'AppRun')
                
                # 创建desktop文件
                desktop_content = """[Desktop Entry]
Name=CAJanus
Exec=AppRun
Icon=cajanus
Type=Application
Categories=Education;Development;
Comment=Device Fingerprint Identification and Modification Tool
"""
                with open(appdir / 'cajanus.desktop', 'w') as f:
                    f.write(desktop_content)
                
                # 复制图标
                if (Path('resources/icons/app.png')).exists():
                    shutil.copy2('resources/icons/app.png', appdir / 'cajanus.png')

# 如果直接运行此文件，执行构建后处理
if __name__ == '__main__':
    post_build()
