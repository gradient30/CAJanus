#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows设备指纹管理器
整合网络管理、WMI接口和注册表操作，提供完整的设备指纹管理功能
"""

import uuid
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.interfaces import IDeviceFingerprintManager, NetworkAdapter
from core.logger import get_logger
from core.exceptions import OperationError, NetworkAdapterError
from .network_manager import get_network_manager
from .wmi_manager import get_wmi_manager
from .registry_manager import get_registry_manager
from .permission_manager import WindowsPermissionManager

class WindowsFingerprintManager(IDeviceFingerprintManager):
    """Windows设备指纹管理器"""
    
    def __init__(self):
        self.logger = get_logger("windows_fingerprint")
        self.network_manager = get_network_manager()
        self.wmi_manager = get_wmi_manager()
        self.registry_manager = get_registry_manager()
        self.permission_manager = WindowsPermissionManager()
        
        self.logger.info("Windows设备指纹管理器初始化完成")
    
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
            if not self.permission_manager.check_admin_privileges():
                raise OperationError("修改MAC地址需要管理员权限")
            
            # 验证操作权限
            if not self.permission_manager.validate_permissions_for_operation('modify_mac_address'):
                raise OperationError("权限验证失败")
            
            return self.network_manager.modify_mac_address(adapter_id, new_mac)
            
        except Exception as e:
            self.logger.error(f"修改MAC地址失败: {e}")
            raise OperationError(f"修改MAC地址失败: {e}")
    
    def restore_original_mac(self, adapter_id: str) -> bool:
        """恢复网卡原始MAC地址"""
        try:
            # 检查权限
            if not self.permission_manager.check_admin_privileges():
                raise OperationError("恢复MAC地址需要管理员权限")
            
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
        """获取机器GUID"""
        try:
            return self.wmi_manager.get_machine_guid()
        except Exception as e:
            self.logger.error(f"获取机器GUID失败: {e}")
            return None
    
    def modify_machine_guid(self, new_guid: str = None) -> bool:
        """修改机器GUID"""
        try:
            # 检查权限
            if not self.permission_manager.check_admin_privileges():
                raise OperationError("修改机器GUID需要管理员权限")
            
            # 验证操作权限
            if not self.permission_manager.validate_permissions_for_operation('modify_machine_guid'):
                raise OperationError("权限验证失败")
            
            return self.wmi_manager.modify_machine_guid(new_guid)
            
        except Exception as e:
            self.logger.error(f"修改机器GUID失败: {e}")
            raise OperationError(f"修改机器GUID失败: {e}")
    
    def get_volume_serial_numbers(self) -> Dict[str, str]:
        """获取磁盘卷序列号"""
        try:
            return self.wmi_manager.get_volume_serial_numbers()
        except Exception as e:
            self.logger.error(f"获取磁盘卷序列号失败: {e}")
            return {}
    
    def modify_volume_serial(self, drive: str, new_serial: str) -> bool:
        """修改磁盘卷序列号"""
        try:
            # 检查权限
            if not self.permission_manager.check_admin_privileges():
                raise OperationError("修改磁盘卷序列号需要管理员权限")
            
            # 验证操作权限
            if not self.permission_manager.validate_permissions_for_operation('modify_volume_serial'):
                raise OperationError("权限验证失败")
            
            # 注意：这是一个高风险操作，需要特别小心
            self.logger.warning(f"尝试修改磁盘卷序列号: {drive} -> {new_serial}")
            
            # 这里应该实现具体的磁盘卷序列号修改逻辑
            # 由于风险极高，暂时返回False，表示不支持
            self.logger.error("磁盘卷序列号修改功能暂未实现（风险过高）")
            return False
            
        except Exception as e:
            self.logger.error(f"修改磁盘卷序列号失败: {e}")
            raise OperationError(f"修改磁盘卷序列号失败: {e}")
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        try:
            # 获取基本硬件信息
            hardware_info = self.wmi_manager.get_hardware_info()
            
            # 获取系统信息
            system_info = self.wmi_manager.get_system_info()
            
            # 合并信息
            complete_info = {
                'hardware': hardware_info,
                'system': system_info,
                'machine_guid': self.get_machine_guid(),
                'volume_serials': self.get_volume_serial_numbers()
            }
            
            return complete_info
            
        except Exception as e:
            self.logger.error(f"获取硬件信息失败: {e}")
            return {}
    
    def get_system_fingerprint(self) -> Dict[str, Any]:
        """获取完整的系统指纹信息"""
        try:
            fingerprint = {
                'timestamp': self.wmi_manager._execute_wmi_query('os', ['LocalDateTime'])[0].get('LocalDateTime', ''),
                'network_adapters': [],
                'machine_guid': self.get_machine_guid(),
                'volume_serials': self.get_volume_serial_numbers(),
                'hardware_info': self.get_hardware_info(),
                'permission_info': self.permission_manager.get_permission_info()
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
                    'can_modify': adapter.can_modify
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
            backup_id = f"fingerprint_{fingerprint.get('timestamp', '').replace(':', '').replace('.', '')}"
            if not backup_id or backup_id == "fingerprint_":
                backup_id = f"fingerprint_{uuid.uuid4().hex[:8]}"
            
            # 保存备份文件
            backup_file = self.registry_manager.backup_dir.parent / f"{backup_id}.json"
            
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
            
            # 验证机器GUID修改
            if 'machine_guid' in changes:
                try:
                    uuid.UUID(changes['machine_guid'])
                    validation_result['warnings'].append("修改机器GUID可能影响系统激活和某些应用程序")
                    validation_result['risk_level'] = 'high'
                except ValueError:
                    validation_result['errors'].append(f"无效的GUID格式: {changes['machine_guid']}")
                    validation_result['valid'] = False
            
            # 验证卷序列号修改
            if 'volume_serial_changes' in changes:
                validation_result['errors'].append("磁盘卷序列号修改功能暂未实现（风险过高）")
                validation_result['valid'] = False
                validation_result['risk_level'] = 'critical'
            
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
            
            # 应用机器GUID修改
            if 'machine_guid' in changes:
                try:
                    success = self.modify_machine_guid(changes['machine_guid'])
                    results['machine_guid'] = success
                except Exception as e:
                    self.logger.error(f"修改机器GUID失败: {e}")
                    results['machine_guid'] = False
            
            self.logger.info(f"指纹修改完成，结果: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"应用指纹修改失败: {e}")
            raise OperationError(f"应用指纹修改失败: {e}")

# 全局Windows设备指纹管理器实例
_windows_fingerprint_manager: Optional[WindowsFingerprintManager] = None

def get_windows_fingerprint_manager() -> WindowsFingerprintManager:
    """获取全局Windows设备指纹管理器实例"""
    global _windows_fingerprint_manager
    if _windows_fingerprint_manager is None:
        _windows_fingerprint_manager = WindowsFingerprintManager()
    return _windows_fingerprint_manager
