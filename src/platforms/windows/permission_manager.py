#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows权限管理器实现
处理Windows平台的权限检查和提升
"""

import os
import sys
import ctypes
import subprocess
import platform as platform_module
from ctypes import wintypes
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.interfaces import IPermissionManager
from core.exceptions import PermissionError
from core.logger import get_logger

class WindowsPermissionManager(IPermissionManager):
    """Windows权限管理器"""
    
    def __init__(self):
        self.logger = get_logger("windows_permission")
        self.logger.info("初始化Windows权限管理器")
    
    def check_admin_privileges(self) -> bool:
        """检查是否具有管理员权限"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            self.logger.error(f"检查管理员权限失败: {e}")
            return False
    
    def request_elevation(self) -> bool:
        """请求权限提升"""
        try:
            if self.check_admin_privileges():
                self.logger.info("已具有管理员权限")
                return True
            
            self.logger.info("请求管理员权限提升")
            
            # 获取当前脚本路径
            script_path = sys.executable
            params = ' '.join(sys.argv)
            
            # 使用ShellExecute请求管理员权限
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", script_path, params, None, 1
            )
            
            # 如果成功启动了提升权限的进程，当前进程应该退出
            if result > 32:
                self.logger.info("权限提升请求已发送，当前进程将退出")
                sys.exit(0)
            else:
                self.logger.error(f"权限提升失败，错误代码: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"请求权限提升失败: {e}")
            return False
    
    def get_current_user(self) -> str:
        """获取当前用户名"""
        try:
            return os.getenv('USERNAME', 'Unknown')
        except Exception as e:
            self.logger.error(f"获取当前用户失败: {e}")
            return 'Unknown'
    
    def check_registry_access(self, registry_path: str) -> bool:
        """检查注册表访问权限"""
        try:
            import winreg
            
            # 尝试打开注册表键
            if registry_path.startswith('HKEY_LOCAL_MACHINE'):
                root_key = winreg.HKEY_LOCAL_MACHINE
                sub_key = registry_path.replace('HKEY_LOCAL_MACHINE\\', '')
            elif registry_path.startswith('HKEY_CURRENT_USER'):
                root_key = winreg.HKEY_CURRENT_USER
                sub_key = registry_path.replace('HKEY_CURRENT_USER\\', '')
            else:
                self.logger.error(f"不支持的注册表根键: {registry_path}")
                return False
            
            with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ):
                return True
                
        except FileNotFoundError:
            self.logger.warning(f"注册表键不存在: {registry_path}")
            return False
        except PermissionError:
            self.logger.warning(f"注册表访问权限不足: {registry_path}")
            return False
        except Exception as e:
            self.logger.error(f"检查注册表访问权限失败: {e}")
            return False
    
    def check_registry_write_access(self, registry_path: str) -> bool:
        """检查注册表写入权限"""
        try:
            import winreg
            
            if registry_path.startswith('HKEY_LOCAL_MACHINE'):
                root_key = winreg.HKEY_LOCAL_MACHINE
                sub_key = registry_path.replace('HKEY_LOCAL_MACHINE\\', '')
            elif registry_path.startswith('HKEY_CURRENT_USER'):
                root_key = winreg.HKEY_CURRENT_USER
                sub_key = registry_path.replace('HKEY_CURRENT_USER\\', '')
            else:
                return False
            
            with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_WRITE):
                return True
                
        except PermissionError:
            return False
        except Exception as e:
            self.logger.error(f"检查注册表写入权限失败: {e}")
            return False
    
    def check_file_access(self, file_path: str, access_mode: str = 'r') -> bool:
        """检查文件访问权限"""
        try:
            mode_map = {
                'r': os.R_OK,
                'w': os.W_OK,
                'x': os.X_OK,
                'rw': os.R_OK | os.W_OK
            }
            
            access_flag = mode_map.get(access_mode, os.R_OK)
            return os.access(file_path, access_flag)
            
        except Exception as e:
            self.logger.error(f"检查文件访问权限失败: {e}")
            return False
    
    def get_required_permissions(self, operation: str) -> List[str]:
        """获取操作所需的权限列表"""
        permission_map = {
            'modify_mac_address': ['管理员权限', '注册表写入权限'],
            'modify_machine_guid': ['管理员权限', '注册表写入权限'],
            'modify_volume_serial': ['管理员权限', '磁盘访问权限'],
            'delete_file': ['文件写入权限'],
            'modify_registry': ['管理员权限', '注册表写入权限']
        }
        
        return permission_map.get(operation, [])
    
    def validate_permissions_for_operation(self, operation: str) -> bool:
        """验证操作所需的权限"""
        required_permissions = self.get_required_permissions(operation)
        
        for permission in required_permissions:
            if permission == '管理员权限':
                if not self.check_admin_privileges():
                    self.logger.warning(f"操作 {operation} 需要管理员权限")
                    return False
            elif permission == '注册表写入权限':
                # 这里可以添加更具体的注册表权限检查
                if not self.check_admin_privileges():
                    self.logger.warning(f"操作 {operation} 需要注册表写入权限")
                    return False
        
        return True
    
    def get_elevation_command(self, command: str) -> str:
        """获取权限提升后的命令"""
        if self.check_admin_privileges():
            return command
        
        # 返回需要管理员权限运行的命令格式
        return f'powershell -Command "Start-Process cmd -ArgumentList \'/c {command}\' -Verb RunAs"'
    
    def run_as_admin(self, command: str, wait: bool = True) -> bool:
        """以管理员权限运行命令"""
        try:
            if self.check_admin_privileges():
                # 已经是管理员权限，直接运行
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.returncode == 0
            
            # 需要提升权限
            elevated_command = self.get_elevation_command(command)
            result = subprocess.run(elevated_command, shell=True, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"以管理员权限运行命令失败: {e}")
            return False
    
    def check_uac_enabled(self) -> bool:
        """检查UAC是否启用"""
        try:
            import winreg
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System") as key:
                value, _ = winreg.QueryValueEx(key, "EnableLUA")
                return bool(value)
                
        except Exception as e:
            self.logger.error(f"检查UAC状态失败: {e}")
            return True  # 默认假设UAC启用
    
    def get_permission_info(self) -> dict:
        """获取当前权限信息"""
        return {
            'is_admin': self.check_admin_privileges(),
            'current_user': self.get_current_user(),
            'uac_enabled': self.check_uac_enabled(),
            'platform': 'Windows'
        }
