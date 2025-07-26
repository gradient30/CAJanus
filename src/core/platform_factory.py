#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台工厂类
根据当前操作系统创建相应的平台特定实现
"""

import platform as platform_module
from typing import Type, Dict, Any
from .interfaces import (
    IDeviceFingerprintManager, IPermissionManager,
    IFileOperationManager, IEducationHelper
)
from .exceptions import PlatformNotSupportedError
from .logger import get_logger

class PlatformFactory:
    """平台工厂类"""
    
    def __init__(self):
        self.logger = get_logger("platform_factory")
        self.current_platform = platform_module.system()
        self.logger.info(f"检测到操作系统: {self.current_platform}")
        
        # 平台实现类注册表
        self._fingerprint_managers: Dict[str, Type[IDeviceFingerprintManager]] = {}
        self._permission_managers: Dict[str, Type[IPermissionManager]] = {}
        self._file_operation_managers: Dict[str, Type[IFileOperationManager]] = {}
        self._education_helpers: Dict[str, Type[IEducationHelper]] = {}
    
    def register_fingerprint_manager(self, platform_name: str, 
                                   manager_class: Type[IDeviceFingerprintManager]):
        """注册设备指纹管理器实现"""
        self._fingerprint_managers[platform_name] = manager_class
        self.logger.debug(f"注册设备指纹管理器: {platform_name} -> {manager_class.__name__}")
    
    def register_permission_manager(self, platform_name: str,
                                  manager_class: Type[IPermissionManager]):
        """注册权限管理器实现"""
        self._permission_managers[platform_name] = manager_class
        self.logger.debug(f"注册权限管理器: {platform_name} -> {manager_class.__name__}")
    
    def register_file_operation_manager(self, platform_name: str,
                                      manager_class: Type[IFileOperationManager]):
        """注册文件操作管理器实现"""
        self._file_operation_managers[platform_name] = manager_class
        self.logger.debug(f"注册文件操作管理器: {platform_name} -> {manager_class.__name__}")
    
    def register_education_helper(self, platform_name: str,
                                helper_class: Type[IEducationHelper]):
        """注册教育辅助功能实现"""
        self._education_helpers[platform_name] = helper_class
        self.logger.debug(f"注册教育辅助功能: {platform_name} -> {helper_class.__name__}")
    
    def create_fingerprint_manager(self, **kwargs) -> IDeviceFingerprintManager:
        """创建设备指纹管理器"""
        if self.current_platform not in self._fingerprint_managers:
            raise PlatformNotSupportedError(self.current_platform)
        
        manager_class = self._fingerprint_managers[self.current_platform]
        self.logger.info(f"创建设备指纹管理器: {manager_class.__name__}")
        return manager_class(**kwargs)
    
    def create_permission_manager(self, **kwargs) -> IPermissionManager:
        """创建权限管理器"""
        if self.current_platform not in self._permission_managers:
            raise PlatformNotSupportedError(self.current_platform)
        
        manager_class = self._permission_managers[self.current_platform]
        self.logger.info(f"创建权限管理器: {manager_class.__name__}")
        return manager_class(**kwargs)
    
    def create_file_operation_manager(self, **kwargs) -> IFileOperationManager:
        """创建文件操作管理器"""
        if self.current_platform not in self._file_operation_managers:
            raise PlatformNotSupportedError(self.current_platform)
        
        manager_class = self._file_operation_managers[self.current_platform]
        self.logger.info(f"创建文件操作管理器: {manager_class.__name__}")
        return manager_class(**kwargs)
    
    def create_education_helper(self, **kwargs) -> IEducationHelper:
        """创建教育辅助功能"""
        if self.current_platform not in self._education_helpers:
            raise PlatformNotSupportedError(self.current_platform)
        
        helper_class = self._education_helpers[self.current_platform]
        self.logger.info(f"创建教育辅助功能: {helper_class.__name__}")
        return helper_class(**kwargs)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """获取平台信息"""
        return {
            'system': platform_module.system(),
            'release': platform_module.release(),
            'version': platform_module.version(),
            'machine': platform_module.machine(),
            'processor': platform_module.processor(),
            'architecture': platform_module.architecture(),
            'python_version': platform_module.python_version()
        }
    
    def is_supported_platform(self) -> bool:
        """检查当前平台是否受支持"""
        return self.current_platform in ['Windows', 'Darwin']
    
    def get_supported_platforms(self) -> list:
        """获取支持的平台列表"""
        return ['Windows', 'Darwin']
    
    def get_platform_capabilities(self) -> Dict[str, Dict[str, bool]]:
        """获取平台功能支持情况"""
        capabilities = {
            'Windows': {
                'mac_address_modification': True,
                'volume_serial_modification': True,
                'machine_guid_modification': True,
                'registry_access': True,
                'wmi_access': True,
                'admin_elevation': True
            },
            'Darwin': {
                'mac_address_modification': True,
                'volume_serial_modification': False,  # 风险太高，暂不支持
                'machine_guid_modification': False,   # macOS没有对应概念
                'ioreg_access': True,
                'sudo_elevation': True,
                'sip_compatibility': True
            }
        }
        
        return capabilities.get(self.current_platform, {})

# 全局平台工厂实例
_platform_factory: PlatformFactory = None

def get_platform_factory() -> PlatformFactory:
    """获取全局平台工厂实例"""
    global _platform_factory
    if _platform_factory is None:
        _platform_factory = PlatformFactory()
        # 确保平台实现已注册
        try:
            auto_register_implementations()
        except Exception as e:
            logger = get_logger("platform_factory")
            logger.error(f"延迟注册平台实现失败: {e}")
    return _platform_factory

def auto_register_implementations():
    """自动注册平台实现"""
    factory = get_platform_factory()
    
    try:
        # 尝试导入并注册Windows实现
        if factory.current_platform == 'Windows':
            try:
                # 使用绝对导入路径
                import sys
                from pathlib import Path

                # 确保可以导入platforms模块
                current_dir = Path(__file__).parent.parent
                if str(current_dir) not in sys.path:
                    sys.path.insert(0, str(current_dir))

                from platforms.windows.fingerprint_manager import WindowsFingerprintManager
                from platforms.windows.permission_manager import WindowsPermissionManager

                factory.register_fingerprint_manager('Windows', WindowsFingerprintManager)
                factory.register_permission_manager('Windows', WindowsPermissionManager)

                factory.logger.info("Windows平台实现注册完成")

            except ImportError as e:
                factory.logger.warning(f"Windows平台实现导入失败: {e}")
            except Exception as e:
                factory.logger.error(f"Windows平台实现注册失败: {e}")
        
        # 尝试导入并注册macOS实现
        elif factory.current_platform == 'Darwin':
            try:
                # 使用绝对导入路径
                import sys
                from pathlib import Path

                # 确保可以导入platforms模块
                current_dir = Path(__file__).parent.parent
                if str(current_dir) not in sys.path:
                    sys.path.insert(0, str(current_dir))

                from platforms.macos.fingerprint_manager import MacOSFingerprintManager
                from platforms.macos.permission_manager import MacOSPermissionManager

                factory.register_fingerprint_manager('Darwin', MacOSFingerprintManager)
                factory.register_permission_manager('Darwin', MacOSPermissionManager)

                factory.logger.info("macOS平台实现注册完成")

            except ImportError as e:
                factory.logger.warning(f"macOS平台实现导入失败: {e}")
            except Exception as e:
                factory.logger.error(f"macOS平台实现注册失败: {e}")
        
        # 注册通用教育辅助功能
        try:
            from ..utils.education_helper import EducationHelper
            factory.register_education_helper('Windows', EducationHelper)
            factory.register_education_helper('Darwin', EducationHelper)
            factory.logger.info("教育辅助功能注册完成")
            
        except ImportError as e:
            factory.logger.warning(f"教育辅助功能导入失败: {e}")
            
    except Exception as e:
        factory.logger.error(f"自动注册平台实现失败: {e}")

# 在模块加载时自动注册实现
try:
    auto_register_implementations()
except Exception as e:
    # 如果自动注册失败，记录错误但不影响模块加载
    logger = get_logger("platform_factory")
    logger.error(f"自动注册平台实现时发生错误: {e}")
