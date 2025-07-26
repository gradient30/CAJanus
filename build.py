#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAJanus构建脚本
自动化构建和打包流程
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from datetime import datetime

# 项目信息
PROJECT_NAME = "CAJanus"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "设备指纹识别与修改工具"

# 路径配置
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
DOCS_DIR = PROJECT_ROOT / "docs"

class BuildError(Exception):
    """构建错误异常"""
    pass

class Builder:
    """构建器类"""
    
    def __init__(self, args):
        self.args = args
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        print(f"🚀 开始构建 {PROJECT_NAME} v{PROJECT_VERSION}")
        print(f"📋 平台: {self.platform} ({self.arch})")
        print(f"🐍 Python: {self.python_version}")
        print("-" * 50)
    
    def clean(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        dirs_to_clean = [BUILD_DIR, DIST_DIR]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   删除: {dir_path}")
        
        # 清理Python缓存
        for root, dirs, files in os.walk(PROJECT_ROOT):
            for dir_name in dirs[:]:
                if dir_name == '__pycache__':
                    shutil.rmtree(Path(root) / dir_name)
                    dirs.remove(dir_name)
            for file_name in files:
                if file_name.endswith('.pyc'):
                    os.remove(Path(root) / file_name)
        
        print("✅ 清理完成")
    
    def check_dependencies(self):
        """检查构建依赖"""
        print("🔍 检查构建依赖...")
        
        required_packages = [
            'PyQt5',
            'psutil', 
            'PyYAML',
            'pyinstaller'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            raise BuildError(f"缺少依赖包: {', '.join(missing_packages)}")
        
        print("✅ 依赖检查完成")
    
    def run_tests(self):
        """运行测试"""
        if self.args.skip_tests:
            print("⏭️  跳过测试")
            return
        
        print("🧪 运行测试...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = str(SRC_DIR)
        
        # 运行测试
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/', '-v', '--tb=short'
            ], cwd=PROJECT_ROOT, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ 测试失败:")
                print(result.stdout)
                print(result.stderr)
                if not self.args.ignore_test_failures:
                    raise BuildError("测试失败，构建终止")
            else:
                print("✅ 测试通过")
                
        except FileNotFoundError:
            print("⚠️  pytest未找到，跳过测试")
    
    def build_executable(self):
        """构建可执行文件"""
        print("🔨 构建可执行文件...")
        
        # PyInstaller命令
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'build.spec'
        ]
        
        if self.args.debug:
            cmd.append('--debug=all')
        
        # 运行PyInstaller
        try:
            result = subprocess.run(
                cmd, cwd=PROJECT_ROOT, 
                capture_output=not self.args.verbose,
                text=True
            )
            
            if result.returncode != 0:
                if not self.args.verbose:
                    print("❌ 构建失败:")
                    print(result.stdout)
                    print(result.stderr)
                raise BuildError("PyInstaller构建失败")
            
            print("✅ 可执行文件构建完成")
            
        except FileNotFoundError:
            raise BuildError("PyInstaller未找到，请安装: pip install pyinstaller")
    
    def create_package(self):
        """创建发布包"""
        print("📦 创建发布包...")
        
        # 确定包名
        package_name = f"{PROJECT_NAME}-{PROJECT_VERSION}-{self.platform}"
        if self.arch in ['x86_64', 'amd64']:
            package_name += "-x64"
        elif self.arch in ['i386', 'i686']:
            package_name += "-x86"
        else:
            package_name += f"-{self.arch}"
        
        # 创建包目录
        package_dir = DIST_DIR / package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir(parents=True)
        
        # 复制可执行文件
        if self.platform == 'windows':
            exe_name = f"{PROJECT_NAME}.exe"
            src_exe = DIST_DIR / exe_name
            if src_exe.exists():
                shutil.copy2(src_exe, package_dir / exe_name)
        
        elif self.platform == 'darwin':
            app_name = f"{PROJECT_NAME}.app"
            src_app = DIST_DIR / app_name
            if src_app.exists():
                shutil.copytree(src_app, package_dir / app_name)
        
        elif self.platform == 'linux':
            exe_name = PROJECT_NAME
            src_exe = DIST_DIR / exe_name
            if src_exe.exists():
                shutil.copy2(src_exe, package_dir / exe_name)
                os.chmod(package_dir / exe_name, 0o755)
        
        # 复制文档和许可证
        docs_to_copy = [
            'README.md',
            'LICENSE', 
            'CHANGELOG.md',
            'docs/用户使用手册.md'
        ]
        
        for doc in docs_to_copy:
            src_doc = PROJECT_ROOT / doc
            if src_doc.exists():
                if src_doc.is_file():
                    shutil.copy2(src_doc, package_dir / src_doc.name)
                else:
                    shutil.copytree(src_doc, package_dir / src_doc.name)
        
        # 创建启动脚本
        self._create_launch_scripts(package_dir)
        
        # 创建压缩包
        if self.args.create_archive:
            self._create_archive(package_dir)
        
        print(f"✅ 发布包创建完成: {package_dir}")
    
    def _create_launch_scripts(self, package_dir):
        """创建启动脚本"""
        if self.platform == 'windows':
            # Windows批处理文件
            bat_content = f"""@echo off
echo 启动 {PROJECT_NAME}...
"{PROJECT_NAME}.exe"
if errorlevel 1 (
    echo 程序异常退出，错误代码: %errorlevel%
    pause
)
"""
            with open(package_dir / f"启动{PROJECT_NAME}.bat", 'w', encoding='gbk') as f:
                f.write(bat_content)
        
        elif self.platform in ['linux', 'darwin']:
            # Shell脚本
            sh_content = f"""#!/bin/bash
echo "启动 {PROJECT_NAME}..."

# 获取脚本所在目录
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"

# 切换到程序目录
cd "$DIR"

# 运行程序
if [ "{self.platform}" = "darwin" ]; then
    open "{PROJECT_NAME}.app"
else
    ./{PROJECT_NAME}
fi

# 检查退出状态
if [ $? -ne 0 ]; then
    echo "程序异常退出，错误代码: $?"
    read -p "按回车键继续..."
fi
"""
            script_path = package_dir / f"启动{PROJECT_NAME}.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(sh_content)
            os.chmod(script_path, 0o755)
    
    def _create_archive(self, package_dir):
        """创建压缩包"""
        print("🗜️  创建压缩包...")
        
        archive_name = package_dir.name
        
        if self.platform == 'windows':
            # 创建ZIP文件
            shutil.make_archive(
                str(DIST_DIR / archive_name),
                'zip',
                str(package_dir.parent),
                package_dir.name
            )
            print(f"   创建: {archive_name}.zip")
        
        else:
            # 创建tar.gz文件
            shutil.make_archive(
                str(DIST_DIR / archive_name),
                'gztar',
                str(package_dir.parent),
                package_dir.name
            )
            print(f"   创建: {archive_name}.tar.gz")
    
    def generate_checksums(self):
        """生成校验和文件"""
        print("🔐 生成校验和...")
        
        import hashlib
        
        checksums = {}
        
        # 遍历dist目录中的文件
        for file_path in DIST_DIR.rglob('*'):
            if file_path.is_file() and not file_path.name.endswith('.txt'):
                # 计算SHA256
                sha256_hash = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                
                rel_path = file_path.relative_to(DIST_DIR)
                checksums[str(rel_path)] = sha256_hash.hexdigest()
        
        # 写入校验和文件
        checksum_file = DIST_DIR / 'checksums.txt'
        with open(checksum_file, 'w', encoding='utf-8') as f:
            f.write(f"# {PROJECT_NAME} v{PROJECT_VERSION} 校验和\n")
            f.write(f"# 生成时间: {datetime.now().isoformat()}\n")
            f.write(f"# 平台: {self.platform} ({self.arch})\n\n")
            
            for file_path, checksum in sorted(checksums.items()):
                f.write(f"{checksum}  {file_path}\n")
        
        print(f"✅ 校验和文件: {checksum_file}")
    
    def build(self):
        """执行完整构建流程"""
        try:
            if self.args.clean:
                self.clean()
            
            self.check_dependencies()
            self.run_tests()
            self.build_executable()
            
            if self.args.package:
                self.create_package()
                self.generate_checksums()
            
            print("\n🎉 构建完成!")
            print(f"📁 输出目录: {DIST_DIR}")
            
        except BuildError as e:
            print(f"\n❌ 构建失败: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n⏹️  构建被用户中断")
            sys.exit(1)
        except Exception as e:
            print(f"\n💥 意外错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description=f"构建 {PROJECT_NAME}")
    
    parser.add_argument('--clean', action='store_true', 
                       help='构建前清理目录')
    parser.add_argument('--skip-tests', action='store_true',
                       help='跳过测试')
    parser.add_argument('--ignore-test-failures', action='store_true',
                       help='忽略测试失败')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细输出')
    parser.add_argument('--package', action='store_true',
                       help='创建发布包')
    parser.add_argument('--create-archive', action='store_true',
                       help='创建压缩包')
    
    args = parser.parse_args()
    
    # 创建构建器并执行构建
    builder = Builder(args)
    builder.build()

if __name__ == '__main__':
    main()
