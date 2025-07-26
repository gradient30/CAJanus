#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAJanus环境检查脚本
检查运行环境是否满足要求
"""

import sys
import platform
import subprocess
import importlib
import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Any

# 颜色输出支持
class Colors:
    """终端颜色常量"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colored_print(text: str, color: str = Colors.WHITE, bold: bool = False):
    """彩色打印"""
    if bold:
        color = Colors.BOLD + color
    print(f"{color}{text}{Colors.END}")

def print_header(title: str):
    """打印标题"""
    colored_print(f"\n{'='*60}", Colors.CYAN, bold=True)
    colored_print(f" {title}", Colors.CYAN, bold=True)
    colored_print(f"{'='*60}", Colors.CYAN, bold=True)

def print_success(message: str):
    """打印成功信息"""
    colored_print(f"✅ {message}", Colors.GREEN)

def print_warning(message: str):
    """打印警告信息"""
    colored_print(f"⚠️  {message}", Colors.YELLOW)

def print_error(message: str):
    """打印错误信息"""
    colored_print(f"❌ {message}", Colors.RED)

def print_info(message: str):
    """打印信息"""
    colored_print(f"ℹ️  {message}", Colors.BLUE)

class EnvironmentChecker:
    """环境检查器"""
    
    def __init__(self):
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.system_info: Dict[str, Any] = {}
        
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print_header("Python环境检查")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        print_info(f"Python版本: {version_str}")
        print_info(f"Python路径: {sys.executable}")
        print_info(f"平台: {platform.platform()}")
        
        self.system_info.update({
            'python_version': version_str,
            'python_path': sys.executable,
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'machine': platform.machine()
        })
        
        # 检查版本要求
        if version.major != 3:
            print_error(f"需要Python 3.x，当前版本: {version.major}.{version.minor}")
            self.issues.append("Python版本不兼容")
            return False
        
        if version.minor < 8:
            print_error(f"需要Python 3.8或更高版本，当前版本: {version.major}.{version.minor}")
            self.issues.append("Python版本过低")
            return False
        
        print_success(f"Python版本检查通过: {version_str}")
        return True
    
    def check_required_packages(self) -> bool:
        """检查必需的包"""
        print_header("依赖包检查")
        
        required_packages = [
            ('PyQt5', '5.15.0', 'GUI框架'),
            ('psutil', '5.8.0', '系统监控'),
            ('PyYAML', '6.0', '配置文件处理'),
            ('requests', '2.25.0', 'HTTP请求'),
            ('cryptography', '3.0.0', '加密支持'),
            ('packaging', '20.0', '版本管理'),
        ]
        
        all_ok = True
        
        for package_name, min_version, description in required_packages:
            try:
                # 尝试导入包
                module_name = package_name.lower().replace('-', '_')
                if module_name == 'pyqt5':
                    module_name = 'PyQt5.QtCore'
                elif module_name == 'pyyaml':
                    module_name = 'yaml'

                module = importlib.import_module(module_name)
                
                # 获取版本信息
                version = getattr(module, '__version__', 'unknown')
                if version == 'unknown' and hasattr(module, 'PYQT_VERSION_STR'):
                    version = module.PYQT_VERSION_STR
                
                print_success(f"{package_name}: {version} ({description})")
                
            except ImportError as e:
                print_error(f"{package_name}: 未安装 ({description})")
                print_info(f"   安装命令: pip install {package_name}>={min_version}")
                self.issues.append(f"缺少依赖包: {package_name}")
                all_ok = False
            except Exception as e:
                print_warning(f"{package_name}: 检查失败 - {e}")
                self.warnings.append(f"包检查异常: {package_name}")
        
        return all_ok
    
    def check_optional_packages(self) -> bool:
        """检查可选包"""
        print_header("可选依赖检查")
        
        optional_packages = [
            ('pytest', '测试框架'),
            ('pylint', '代码检查'),
            ('black', '代码格式化'),
            ('pyinstaller', '打包工具'),
        ]
        
        for package_name, description in optional_packages:
            try:
                importlib.import_module(package_name.replace('-', '_'))
                print_success(f"{package_name}: 已安装 ({description})")
            except ImportError:
                print_warning(f"{package_name}: 未安装 ({description})")
                print_info(f"   安装命令: pip install {package_name}")
        
        return True
    
    def check_system_permissions(self) -> bool:
        """检查系统权限"""
        print_header("系统权限检查")
        
        system = platform.system()
        
        if system == "Windows":
            return self._check_windows_permissions()
        elif system == "Darwin":
            return self._check_macos_permissions()
        elif system == "Linux":
            return self._check_linux_permissions()
        else:
            print_warning(f"未知操作系统: {system}")
            return True
    
    def _check_windows_permissions(self) -> bool:
        """检查Windows权限"""
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            
            if is_admin:
                print_success("Windows管理员权限: 已获取")
            else:
                print_warning("Windows管理员权限: 未获取")
                print_info("   某些功能可能需要管理员权限")
                print_info("   右键点击程序，选择'以管理员身份运行'")
                self.warnings.append("缺少管理员权限")
            
            # 检查注册表访问
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE")
                winreg.CloseKey(key)
                print_success("注册表访问: 正常")
            except Exception as e:
                print_error(f"注册表访问: 失败 - {e}")
                self.issues.append("注册表访问失败")
            
        except Exception as e:
            print_error(f"权限检查失败: {e}")
            self.issues.append("权限检查异常")
            return False
        
        return True
    
    def _check_macos_permissions(self) -> bool:
        """检查macOS权限"""
        import os
        
        if os.geteuid() == 0:
            print_success("Root权限: 已获取")
        else:
            print_warning("Root权限: 未获取")
            print_info("   某些功能可能需要sudo权限")
            self.warnings.append("缺少root权限")
        
        # 检查网络配置权限
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success("网络配置访问: 正常")
            else:
                print_warning("网络配置访问: 受限")
        except Exception as e:
            print_error(f"网络配置检查失败: {e}")
        
        return True
    
    def _check_linux_permissions(self) -> bool:
        """检查Linux权限"""
        import os
        
        if os.geteuid() == 0:
            print_success("Root权限: 已获取")
        else:
            print_warning("Root权限: 未获取")
            print_info("   某些功能可能需要sudo权限")
            self.warnings.append("缺少root权限")
        
        # 检查网络接口访问
        try:
            if Path('/proc/net/dev').exists():
                print_success("网络接口访问: 正常")
            else:
                print_error("网络接口访问: 失败")
                self.issues.append("无法访问网络接口")
        except Exception as e:
            print_error(f"网络接口检查失败: {e}")
        
        return True
    
    def check_disk_space(self) -> bool:
        """检查磁盘空间"""
        print_header("磁盘空间检查")
        
        try:
            current_dir = Path.cwd()
            total, used, free = shutil.disk_usage(current_dir)
            
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            used_percent = (used / total) * 100
            
            print_info(f"当前目录: {current_dir}")
            print_info(f"总空间: {total_gb:.1f} GB")
            print_info(f"已使用: {used_percent:.1f}%")
            print_info(f"可用空间: {free_gb:.1f} GB")
            
            if free_gb >= 2.0:
                print_success(f"磁盘空间充足: {free_gb:.1f} GB")
            elif free_gb >= 1.0:
                print_warning(f"磁盘空间较少: {free_gb:.1f} GB")
                self.warnings.append("磁盘空间不足")
            else:
                print_error(f"磁盘空间严重不足: {free_gb:.1f} GB")
                self.issues.append("磁盘空间不足")
                return False
            
        except Exception as e:
            print_error(f"磁盘空间检查失败: {e}")
            self.issues.append("磁盘空间检查异常")
            return False
        
        return True
    
    def check_network_connectivity(self) -> bool:
        """检查网络连接（可选）"""
        print_header("网络连接检查")
        
        try:
            import socket
            
            # 测试DNS解析
            socket.gethostbyname('www.google.com')
            print_success("网络连接: 正常")
            
        except socket.gaierror:
            print_warning("网络连接: 无法连接到互联网")
            print_info("   程序可以离线运行，但无法检查更新")
            self.warnings.append("网络连接异常")
        except Exception as e:
            print_warning(f"网络检查失败: {e}")
        
        return True
    
    def check_gui_support(self) -> bool:
        """检查GUI支持"""
        print_header("GUI环境检查")
        
        try:
            # 检查显示环境
            if platform.system() == "Linux":
                display = os.environ.get('DISPLAY')
                if not display:
                    print_error("未检测到X11显示环境")
                    print_info("   请确保在图形界面环境中运行")
                    self.issues.append("缺少GUI环境")
                    return False
                else:
                    print_success(f"X11显示环境: {display}")
            
            # 尝试创建QApplication
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app is None:
                    app = QApplication([])
                print_success("PyQt5 GUI支持: 正常")
                return True
            except Exception as e:
                print_error(f"PyQt5 GUI初始化失败: {e}")
                self.issues.append("GUI初始化失败")
                return False
                
        except Exception as e:
            print_error(f"GUI环境检查失败: {e}")
            self.issues.append("GUI环境检查异常")
            return False
    
    def generate_report(self):
        """生成检查报告"""
        print_header("环境检查报告")
        
        # 系统信息
        print_info("系统信息:")
        for key, value in self.system_info.items():
            print(f"   {key}: {value}")
        
        # 问题总结
        if self.issues:
            print_error(f"发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print_warning(f"发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # 总体结果
        if not self.issues:
            if not self.warnings:
                print_success("🎉 环境检查完全通过！")
                print_info("您的环境已准备就绪，可以运行CAJanus")
            else:
                print_warning("⚠️  环境检查基本通过，但有一些警告")
                print_info("程序可以运行，但某些功能可能受限")
        else:
            print_error("❌ 环境检查未通过")
            print_info("请解决上述问题后重新运行检查")
        
        return len(self.issues) == 0
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        colored_print("🔍 CAJanus环境检查工具", Colors.MAGENTA, bold=True)
        colored_print("检查运行环境是否满足要求...\n", Colors.WHITE)
        
        checks = [
            self.check_python_version,
            self.check_required_packages,
            self.check_optional_packages,
            self.check_system_permissions,
            self.check_disk_space,
            self.check_network_connectivity,
            self.check_gui_support,
        ]
        
        for check in checks:
            try:
                check()
            except KeyboardInterrupt:
                print_error("\n检查被用户中断")
                return False
            except Exception as e:
                print_error(f"检查过程中发生错误: {e}")
                self.issues.append(f"检查异常: {e}")
        
        return self.generate_report()

def main():
    """主函数"""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
