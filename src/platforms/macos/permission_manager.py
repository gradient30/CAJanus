#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS权限管理器实现
处理macOS平台的权限检查和sudo权限管理
"""

import os
import subprocess
import getpass
from typing import List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.interfaces import IPermissionManager
from core.exceptions import PermissionError
from core.logger import get_logger

class MacOSPermissionManager(IPermissionManager):
    """macOS权限管理器"""
    
    def __init__(self):
        self.logger = get_logger("macos_permission")
        self.logger.info("初始化macOS权限管理器")
    
    def check_admin_privileges(self) -> bool:
        """检查是否具有管理员权限（root权限）"""
        try:
            return os.geteuid() == 0
        except Exception as e:
            self.logger.error(f"检查管理员权限失败: {e}")
            return False
    
    def check_sudo_privileges(self) -> bool:
        """检查是否可以使用sudo权限"""
        try:
            # 尝试执行一个需要sudo的命令，但不实际执行
            result = subprocess.run(['sudo', '-n', 'echo', 'test'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"检查sudo权限失败: {e}")
            return False
    
    def request_elevation(self) -> bool:
        """请求权限提升（通过sudo）"""
        try:
            if self.check_admin_privileges():
                self.logger.info("已具有root权限")
                return True
            
            # 检查是否可以使用sudo
            if not self.check_sudo_privileges():
                self.logger.warning("当前用户无法使用sudo权限")
                return False
            
            self.logger.info("sudo权限可用")
            return True
            
        except Exception as e:
            self.logger.error(f"请求权限提升失败: {e}")
            return False
    
    def get_current_user(self) -> str:
        """获取当前用户名"""
        try:
            return getpass.getuser()
        except Exception as e:
            self.logger.error(f"获取当前用户失败: {e}")
            return 'Unknown'
    
    def check_file_permissions(self, file_path: str, permission: str = 'r') -> bool:
        """检查文件权限"""
        try:
            mode_map = {
                'r': os.R_OK,
                'w': os.W_OK,
                'x': os.X_OK,
                'rw': os.R_OK | os.W_OK
            }
            
            access_flag = mode_map.get(permission, os.R_OK)
            return os.access(file_path, access_flag)
            
        except Exception as e:
            self.logger.error(f"检查文件权限失败: {e}")
            return False
    
    def check_sip_status(self) -> dict:
        """检查系统完整性保护(SIP)状态"""
        try:
            result = subprocess.run(['csrutil', 'status'], 
                                  capture_output=True, text=True)
            
            sip_info = {
                'enabled': False,
                'status': 'unknown',
                'raw_output': result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            }
            
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                sip_info['status'] = result.stdout.strip()
                sip_info['enabled'] = 'enabled' in output
            else:
                sip_info['status'] = f'error: {result.stderr.strip()}'
            
            return sip_info
            
        except Exception as e:
            self.logger.error(f"检查SIP状态失败: {e}")
            return {
                'enabled': None,
                'status': f'error: {e}',
                'raw_output': ''
            }
    
    def get_required_permissions(self, operation: str) -> List[str]:
        """获取操作所需的权限列表"""
        permission_map = {
            'modify_mac_address': ['sudo权限', '网络接口访问权限'],
            'read_hardware_info': ['系统信息读取权限'],
            'read_ioreg': ['IORegistry读取权限'],
            'modify_network_config': ['sudo权限', '网络配置修改权限'],
            'delete_file': ['文件写入权限'],
            'access_system_info': ['系统信息访问权限']
        }
        
        return permission_map.get(operation, [])
    
    def validate_permissions_for_operation(self, operation: str) -> bool:
        """验证操作所需的权限"""
        required_permissions = self.get_required_permissions(operation)
        
        for permission in required_permissions:
            if permission == 'sudo权限':
                if not self.check_sudo_privileges() and not self.check_admin_privileges():
                    self.logger.warning(f"操作 {operation} 需要sudo权限")
                    return False
            elif permission == '网络接口访问权限':
                # 检查是否可以访问网络接口
                if not self.check_file_permissions('/sbin/ifconfig', 'x'):
                    self.logger.warning(f"操作 {operation} 需要网络接口访问权限")
                    return False
        
        return True
    
    def run_with_sudo(self, command: str, timeout: int = 30) -> tuple:
        """使用sudo权限运行命令"""
        try:
            if isinstance(command, str):
                cmd = ['sudo'] + command.split()
            else:
                cmd = ['sudo'] + command
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"命令执行超时: {command}")
            return False, '', 'Command timeout'
        except Exception as e:
            self.logger.error(f"sudo命令执行失败: {e}")
            return False, '', str(e)
    
    def check_network_interface_access(self) -> bool:
        """检查网络接口访问权限"""
        try:
            # 尝试列出网络接口
            result = subprocess.run(['ifconfig', '-l'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"检查网络接口访问权限失败: {e}")
            return False
    
    def check_ioreg_access(self) -> bool:
        """检查IORegistry访问权限"""
        try:
            # 尝试访问IORegistry
            result = subprocess.run(['ioreg', '-c', 'IOPlatformExpertDevice', '-d', '1'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"检查IORegistry访问权限失败: {e}")
            return False
    
    def get_permission_info(self) -> dict:
        """获取当前权限信息"""
        sip_info = self.check_sip_status()
        
        return {
            'is_root': self.check_admin_privileges(),
            'has_sudo': self.check_sudo_privileges(),
            'current_user': self.get_current_user(),
            'sip_enabled': sip_info['enabled'],
            'sip_status': sip_info['status'],
            'network_access': self.check_network_interface_access(),
            'ioreg_access': self.check_ioreg_access(),
            'platform': 'macOS'
        }
    
    def get_user_groups(self) -> List[str]:
        """获取当前用户所属的组"""
        try:
            result = subprocess.run(['groups'], capture_output=True, text=True)
            if result.returncode == 0:
                groups = result.stdout.strip().split()
                return groups
            return []
            
        except Exception as e:
            self.logger.error(f"获取用户组失败: {e}")
            return []
    
    def is_in_admin_group(self) -> bool:
        """检查当前用户是否在admin组中"""
        try:
            groups = self.get_user_groups()
            return 'admin' in groups
        except Exception as e:
            self.logger.error(f"检查admin组成员身份失败: {e}")
            return False
    
    def check_keychain_access(self) -> bool:
        """检查钥匙串访问权限"""
        try:
            result = subprocess.run(['security', 'list-keychains'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"检查钥匙串访问权限失败: {e}")
            return False
    
    def get_system_version(self) -> dict:
        """获取系统版本信息"""
        try:
            result = subprocess.run(['sw_vers'], capture_output=True, text=True)
            
            version_info = {}
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        version_info[key.strip()] = value.strip()
            
            return version_info
            
        except Exception as e:
            self.logger.error(f"获取系统版本信息失败: {e}")
            return {}

# 全局macOS权限管理器实例
_macos_permission_manager = None

def get_macos_permission_manager() -> MacOSPermissionManager:
    """获取全局macOS权限管理器实例"""
    global _macos_permission_manager
    if _macos_permission_manager is None:
        _macos_permission_manager = MacOSPermissionManager()
    return _macos_permission_manager
