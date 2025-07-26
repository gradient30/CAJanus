#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS设备指纹管理器
整合网络管理、系统信息和权限管理，提供完整的macOS设备指纹管理功能
"""

import uuid
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.interfaces import IDeviceFingerprintManager, NetworkAdapter
from core.logger import get_logger
from core.exceptions import OperationError, NetworkAdapterError
from .network_manager import get_macos_network_manager
from .system_info_manager import get_system_info_manager
from .permission_manager import get_macos_permission_manager

class MacOSFingerprintManager(IDeviceFingerprintManager):
    """macOS设备指纹管理器"""
    
    def __init__(self):
        self.logger = get_logger("macos_fingerprint")
        self.network_manager = get_macos_network_manager()
        self.system_info_manager = get_system_info_manager()
        self.permission_manager = get_macos_permission_manager()
        
        self.logger.info("macOS设备指纹管理器初始化完成")
    
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """获取所有网络适配器信息"""
        try:
            return self.network_manager.get_network_adapters()
        except Exception as e:
            self.logger.error(f"获取网络适配器失败: {e}")
            raise OperationError(f"获取网络适配器失败: {e}")
    
    def get_mac_address(self, adapter_id: str) -> Optional[str]:
        """获取指定网卡的MAC地址"""
        try:
            return self.network_manager.get_current_mac_address(adapter_id)
        except Exception as e:
            self.logger.error(f"获取MAC地址失败: {e}")
            return None
    
    def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
        """修改指定网卡的MAC地址"""
        try:
            # 检查权限
            if not self.permission_manager.validate_permissions_for_operation('modify_mac_address'):
                raise OperationError("修改MAC地址需要sudo权限")
            
            return self.network_manager.modify_mac_address(adapter_id, new_mac)
            
        except Exception as e:
            self.logger.error(f"修改MAC地址失败: {e}")
            raise OperationError(f"修改MAC地址失败: {e}")
    
    def restore_original_mac(self, adapter_id: str) -> bool:
        """恢复网卡原始MAC地址"""
        try:
            # 检查权限
            if not self.permission_manager.validate_permissions_for_operation('modify_mac_address'):
                raise OperationError("恢复MAC地址需要sudo权限")
            
            return self.network_manager.restore_original_mac(adapter_id)
            
        except Exception as e:
            self.logger.error(f"恢复MAC地址失败: {e}")
            raise OperationError(f"恢复MAC地址失败: {e}")
    
    def generate_random_mac(self, vendor_prefix: str = None) -> str:
        """生成随机MAC地址"""
        try:
            return self.network_manager.generate_random_mac(vendor_prefix)
        except Exception as e:
            self.logger.error(f"生成随机MAC地址失败: {e}")
            raise OperationError(f"生成随机MAC地址失败: {e}")
    
    def get_machine_guid(self) -> Optional[str]:
        """获取机器GUID（在macOS上返回硬件UUID）"""
        try:
            # macOS没有Windows的MachineGuid概念，返回硬件UUID
            return self.system_info_manager.get_hardware_uuid()
        except Exception as e:
            self.logger.error(f"获取硬件UUID失败: {e}")
            return None
    
    def modify_machine_guid(self, new_guid: str = None) -> bool:
        """修改机器GUID（macOS不支持此操作）"""
        try:
            # macOS的硬件UUID是只读的，无法修改
            self.logger.warning("macOS不支持修改硬件UUID")
            raise OperationError("macOS不支持修改硬件UUID")
            
        except Exception as e:
            self.logger.error(f"修改硬件UUID失败: {e}")
            raise OperationError(f"修改硬件UUID失败: {e}")
    
    def get_volume_serial_numbers(self) -> Dict[str, str]:
        """获取磁盘卷序列号"""
        try:
            # macOS的卷序列号概念与Windows不同
            # 这里返回文件系统UUID
            volume_serials = {}
            
            storage_info = self.system_info_manager._get_storage_info()
            for storage in storage_info:
                mount_point = storage.get('mount_point', '')
                filesystem = storage.get('filesystem', '')
                if mount_point and filesystem:
                    volume_serials[mount_point] = filesystem
            
            return volume_serials
            
        except Exception as e:
            self.logger.error(f"获取卷序列号失败: {e}")
            return {}
    
    def modify_volume_serial(self, drive: str, new_serial: str) -> bool:
        """修改磁盘卷序列号（macOS不支持此操作）"""
        try:
            # macOS不支持修改文件系统UUID
            self.logger.warning("macOS不支持修改卷序列号")
            raise OperationError("macOS不支持修改卷序列号")
            
        except Exception as e:
            self.logger.error(f"修改卷序列号失败: {e}")
            raise OperationError(f"修改卷序列号失败: {e}")
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        try:
            # 获取基本硬件信息
            hardware_info = self.system_info_manager.get_hardware_info()
            
            # 获取系统信息
            system_info = self.system_info_manager.get_system_info()
            
            # 获取IORegistry信息
            ioreg_info = self.system_info_manager.get_ioreg_info()
            
            # 合并信息
            complete_info = {
                'hardware': hardware_info,
                'system': system_info,
                'ioreg': ioreg_info,
                'hardware_uuid': self.get_machine_guid(),
                'platform_serial': self.system_info_manager.get_platform_serial(),
                'volume_info': self.get_volume_serial_numbers()
            }
            
            return complete_info
            
        except Exception as e:
            self.logger.error(f"获取硬件信息失败: {e}")
            return {}
    
    def get_system_fingerprint(self) -> Dict[str, Any]:
        """获取完整的系统指纹信息"""
        try:
            import datetime
            
            fingerprint = {
                'timestamp': datetime.datetime.now().isoformat(),
                'platform': 'macOS',
                'network_adapters': [],
                'hardware_uuid': self.get_machine_guid(),
                'platform_serial': self.system_info_manager.get_platform_serial(),
                'volume_info': self.get_volume_serial_numbers(),
                'hardware_info': self.get_hardware_info(),
                'permission_info': self.permission_manager.get_permission_info(),
                'ioreg_info': self.system_info_manager.get_ioreg_info()
            }
            
            # 获取网络适配器信息
            adapters = self.get_network_adapters()
            for adapter in adapters:
                fingerprint['network_adapters'].append({
                    'id': adapter.id,
                    'name': adapter.name,
                    'description': adapter.description,
                    'mac_address': adapter.mac_address,
                    'status': adapter.status,
                    'type': adapter.adapter_type.value,
                    'can_modify': adapter.can_modify,
                    'interface_name': adapter.interface_name
                })
            
            self.logger.info("系统指纹信息获取完成")
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"获取系统指纹失败: {e}")
            return {}
    
    def backup_current_fingerprint(self) -> str:
        """备份当前系统指纹"""
        try:
            fingerprint = self.get_system_fingerprint()
            
            # 生成备份ID
            backup_id = f"macos_fingerprint_{fingerprint.get('timestamp', '').replace(':', '').replace('.', '').replace('-', '')}"
            if not backup_id or backup_id == "macos_fingerprint_":
                backup_id = f"macos_fingerprint_{uuid.uuid4().hex[:8]}"
            
            # 保存备份文件
            from core.config_manager import get_config_manager
            config_manager = get_config_manager()
            backup_file = config_manager.get_backup_directory() / f"{backup_id}.json"
            
            import json
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(fingerprint, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"系统指纹备份完成: {backup_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"备份系统指纹失败: {e}")
            raise OperationError(f"备份系统指纹失败: {e}")
    
    def validate_fingerprint_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """验证指纹修改的有效性和风险"""
        try:
            validation_result = {
                'valid': True,
                'warnings': [],
                'errors': [],
                'risk_level': 'low'
            }
            
            # 验证MAC地址修改
            if 'mac_changes' in changes:
                for adapter_id, new_mac in changes['mac_changes'].items():
                    adapter = self.network_manager.get_adapter_by_id(adapter_id)
                    if not adapter:
                        validation_result['errors'].append(f"找不到网络适配器: {adapter_id}")
                        validation_result['valid'] = False
                    elif not adapter.can_modify:
                        validation_result['errors'].append(f"网络适配器不支持修改: {adapter.name}")
                        validation_result['valid'] = False
                    elif not self.network_manager._validate_mac_address(new_mac):
                        validation_result['errors'].append(f"无效的MAC地址格式: {new_mac}")
                        validation_result['valid'] = False
                    else:
                        validation_result['warnings'].append(f"修改MAC地址可能影响网络连接: {adapter.name}")
                        if validation_result['risk_level'] == 'low':
                            validation_result['risk_level'] = 'medium'
            
            # 验证硬件UUID修改
            if 'hardware_uuid' in changes:
                validation_result['errors'].append("macOS不支持修改硬件UUID")
                validation_result['valid'] = False
                validation_result['risk_level'] = 'critical'
            
            # 验证卷序列号修改
            if 'volume_serial_changes' in changes:
                validation_result['errors'].append("macOS不支持修改卷序列号")
                validation_result['valid'] = False
                validation_result['risk_level'] = 'critical'
            
            # 检查权限
            if 'mac_changes' in changes and changes['mac_changes']:
                if not self.permission_manager.validate_permissions_for_operation('modify_mac_address'):
                    validation_result['errors'].append("修改MAC地址需要sudo权限")
                    validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"验证指纹修改失败: {e}")
            return {
                'valid': False,
                'errors': [f"验证失败: {e}"],
                'warnings': [],
                'risk_level': 'critical'
            }
    
    def apply_fingerprint_changes(self, changes: Dict[str, Any]) -> Dict[str, bool]:
        """应用指纹修改"""
        try:
            # 先验证修改
            validation = self.validate_fingerprint_changes(changes)
            if not validation['valid']:
                raise OperationError(f"指纹修改验证失败: {validation['errors']}")
            
            results = {}
            
            # 创建备份
            backup_id = self.backup_current_fingerprint()
            self.logger.info(f"创建备份: {backup_id}")
            
            # 应用MAC地址修改
            if 'mac_changes' in changes:
                for adapter_id, new_mac in changes['mac_changes'].items():
                    try:
                        success = self.modify_mac_address(adapter_id, new_mac)
                        results[f'mac_{adapter_id}'] = success
                    except Exception as e:
                        self.logger.error(f"修改MAC地址失败: {adapter_id} -> {new_mac}, {e}")
                        results[f'mac_{adapter_id}'] = False
            
            # macOS不支持其他类型的修改
            if 'hardware_uuid' in changes:
                results['hardware_uuid'] = False
                self.logger.warning("macOS不支持修改硬件UUID")
            
            if 'volume_serial_changes' in changes:
                results['volume_serial'] = False
                self.logger.warning("macOS不支持修改卷序列号")
            
            self.logger.info(f"指纹修改完成，结果: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"应用指纹修改失败: {e}")
            raise OperationError(f"应用指纹修改失败: {e}")
    
    def get_supported_operations(self) -> List[str]:
        """获取支持的操作列表"""
        return [
            'get_network_adapters',
            'get_mac_address',
            'modify_mac_address',
            'restore_original_mac',
            'generate_random_mac',
            'get_hardware_uuid',
            'get_platform_serial',
            'get_hardware_info',
            'get_system_fingerprint',
            'backup_current_fingerprint'
        ]
    
    def get_unsupported_operations(self) -> List[str]:
        """获取不支持的操作列表"""
        return [
            'modify_machine_guid',
            'modify_volume_serial'
        ]

# 全局macOS设备指纹管理器实例
_macos_fingerprint_manager = None

def get_macos_fingerprint_manager() -> MacOSFingerprintManager:
    """获取全局macOS设备指纹管理器实例"""
    global _macos_fingerprint_manager
    if _macos_fingerprint_manager is None:
        _macos_fingerprint_manager = MacOSFingerprintManager()
    return _macos_fingerprint_manager
