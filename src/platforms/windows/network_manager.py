#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows网络管理器
处理网络适配器信息获取和MAC地址修改
"""

import subprocess
import re
import winreg
from typing import List, Dict, Optional, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.interfaces import NetworkAdapter, AdapterType
from core.logger import get_logger
from core.exceptions import NetworkAdapterError
from .registry_manager import get_registry_manager

class NetworkManager:
    """Windows网络管理器"""
    
    def __init__(self):
        self.logger = get_logger("network_manager")
        self.registry_manager = get_registry_manager()
        
        # 网卡注册表路径
        self.network_class_path = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
        
        self.logger.info("网络管理器初始化完成")
    
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """获取所有网络适配器信息"""
        try:
            adapters = []
            
            # 从WMI获取网卡基本信息
            wmi_adapters = self._get_wmi_adapters()
            
            # 从注册表获取详细配置
            registry_adapters = self._get_registry_adapters()
            
            # 合并信息
            for wmi_adapter in wmi_adapters:
                # 查找对应的注册表信息
                registry_info = None
                for reg_adapter in registry_adapters:
                    if (wmi_adapter.get('mac_address') == reg_adapter.get('original_mac') or
                        wmi_adapter.get('description') == reg_adapter.get('description')):
                        registry_info = reg_adapter
                        break
                
                adapter = NetworkAdapter(
                    id=wmi_adapter.get('device_id', ''),
                    name=wmi_adapter.get('name', ''),
                    description=wmi_adapter.get('description', ''),
                    mac_address=wmi_adapter.get('mac_address', ''),
                    status=wmi_adapter.get('status', 'unknown'),
                    adapter_type=self._determine_adapter_type(wmi_adapter.get('description', '')),
                    can_modify=registry_info is not None,
                    registry_path=registry_info.get('registry_path') if registry_info else None
                )
                
                adapters.append(adapter)
            
            self.logger.info(f"获取到 {len(adapters)} 个网络适配器")
            return adapters
            
        except Exception as e:
            self.logger.error(f"获取网络适配器失败: {e}")
            raise NetworkAdapterError(f"获取网络适配器失败: {e}")
    
    def _get_wmi_adapters(self) -> List[Dict[str, Any]]:
        """通过WMI获取网卡信息"""
        try:
            # 使用更明确的WMI命令格式
            cmd = 'wmic path win32_networkadapter where "MACAddress is not null" get Name,MACAddress,PNPDeviceID,Description,NetEnabled /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk', errors='ignore')

            if result.returncode != 0:
                self.logger.warning(f"WMI命令执行失败，尝试备用方法: {result.stderr}")
                return self._get_wmi_adapters_fallback()

            adapters = []
            lines = result.stdout.strip().split('\n')

            # 查找标题行
            header_line = None
            for i, line in enumerate(lines):
                if 'Description' in line and 'MACAddress' in line and 'Name' in line:
                    header_line = i
                    break

            if header_line is None:
                self.logger.warning("未找到WMI输出标题行，尝试备用方法")
                return self._get_wmi_adapters_fallback()

            # 解析标题获取字段索引
            headers = [h.strip() for h in lines[header_line].split(',')]
            self.logger.debug(f"WMI输出标题: {headers}")

            # 查找字段索引
            try:
                name_idx = headers.index('Name')
                mac_idx = headers.index('MACAddress')
                desc_idx = headers.index('Description')
                device_idx = headers.index('PNPDeviceID')
                enabled_idx = headers.index('NetEnabled')
            except ValueError as e:
                self.logger.error(f"WMI输出格式不符合预期: {e}")
                return self._get_wmi_adapters_fallback()

            # 解析数据行
            for line in lines[header_line + 1:]:
                if not line.strip():
                    continue

                parts = [part.strip() for part in line.split(',')]
                if len(parts) > max(name_idx, mac_idx, desc_idx, device_idx, enabled_idx):
                    mac_address = parts[mac_idx] if mac_idx < len(parts) else ''
                    name = parts[name_idx] if name_idx < len(parts) else ''
                    description = parts[desc_idx] if desc_idx < len(parts) else ''
                    device_id = parts[device_idx] if device_idx < len(parts) else ''
                    enabled = parts[enabled_idx] if enabled_idx < len(parts) else ''

                    # 过滤掉没有MAC地址的虚拟适配器
                    if mac_address and len(mac_address) >= 12:  # 至少12个字符的MAC地址
                        # 标准化MAC地址格式
                        mac_address = self._normalize_mac_address(mac_address)

                        adapters.append({
                            'name': name or description,  # 如果name为空，使用description
                            'description': description,
                            'mac_address': mac_address,
                            'device_id': device_id,
                            'status': 'enabled' if enabled.upper() == 'TRUE' else 'disabled'
                        })

            self.logger.info(f"通过WMI获取到 {len(adapters)} 个网络适配器")
            return adapters

        except Exception as e:
            self.logger.error(f"WMI获取网卡信息失败: {e}")
            return self._get_wmi_adapters_fallback()

    def _get_wmi_adapters_fallback(self) -> List[Dict[str, Any]]:
        """WMI获取网卡信息的备用方法"""
        try:
            # 使用更简单的命令格式
            cmd = 'wmic path win32_networkadapter get Name,MACAddress,Description /format:list'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk', errors='ignore')

            if result.returncode != 0:
                return []

            adapters = []
            current_adapter = {}

            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    if current_adapter and current_adapter.get('mac_address'):
                        adapters.append(current_adapter)
                    current_adapter = {}
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'Name' and value:
                        current_adapter['name'] = value
                    elif key == 'Description' and value:
                        current_adapter['description'] = value
                    elif key == 'MACAddress' and value:
                        current_adapter['mac_address'] = self._normalize_mac_address(value)
                        current_adapter['device_id'] = value  # 临时使用MAC作为ID
                        current_adapter['status'] = 'enabled'

            # 处理最后一个适配器
            if current_adapter and current_adapter.get('mac_address'):
                adapters.append(current_adapter)

            self.logger.info(f"通过备用方法获取到 {len(adapters)} 个网络适配器")
            return adapters

        except Exception as e:
            self.logger.error(f"备用方法获取网卡信息失败: {e}")
            return []

    def _normalize_mac_address(self, mac: str) -> str:
        """标准化MAC地址格式"""
        if not mac:
            return ''

        # 移除所有非十六进制字符
        clean_mac = re.sub(r'[^0-9A-Fa-f]', '', mac)

        # 确保是12位十六进制
        if len(clean_mac) != 12:
            return mac  # 返回原始值，让上层处理

        # 转换为标准格式 XX:XX:XX:XX:XX:XX
        return ':'.join(clean_mac[i:i+2].upper() for i in range(0, 12, 2))
    
    def _get_registry_adapters(self) -> List[Dict[str, Any]]:
        """从注册表获取网卡配置信息"""
        try:
            adapters = []
            
            # 枚举网卡注册表子键
            root_key = winreg.HKEY_LOCAL_MACHINE
            class_path = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            
            with winreg.OpenKey(root_key, class_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.isdigit():  # 只处理数字子键
                            subkey_path = f"{class_path}\\{subkey_name}"
                            adapter_info = self._get_adapter_registry_info(subkey_path)
                            if adapter_info:
                                adapter_info['registry_path'] = f"HKEY_LOCAL_MACHINE\\{subkey_path}"
                                adapters.append(adapter_info)
                        i += 1
                    except OSError:
                        break
            
            return adapters
            
        except Exception as e:
            self.logger.error(f"从注册表获取网卡信息失败: {e}")
            return []
    
    def _get_adapter_registry_info(self, registry_path: str) -> Optional[Dict[str, Any]]:
        """获取单个网卡的注册表信息"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                adapter_info = {}
                
                # 获取驱动描述
                try:
                    adapter_info['description'] = winreg.QueryValueEx(key, "DriverDesc")[0]
                except FileNotFoundError:
                    return None  # 没有驱动描述的不是网卡
                
                # 获取当前MAC地址设置
                try:
                    adapter_info['current_mac'] = winreg.QueryValueEx(key, "NetworkAddress")[0]
                except FileNotFoundError:
                    adapter_info['current_mac'] = None
                
                # 获取原始MAC地址（如果有的话）
                try:
                    adapter_info['original_mac'] = winreg.QueryValueEx(key, "PermanentAddress")[0]
                except FileNotFoundError:
                    adapter_info['original_mac'] = None
                
                return adapter_info
                
        except Exception as e:
            self.logger.debug(f"获取注册表信息失败: {registry_path}, {e}")
            return None
    
    def _determine_adapter_type(self, description: str) -> AdapterType:
        """根据描述判断网卡类型"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['wireless', 'wifi', 'wi-fi', '802.11']):
            return AdapterType.WIRELESS
        elif any(keyword in description_lower for keyword in ['bluetooth', 'bt']):
            return AdapterType.BLUETOOTH
        elif any(keyword in description_lower for keyword in ['virtual', 'vmware', 'virtualbox', 'hyper-v']):
            return AdapterType.VIRTUAL
        elif any(keyword in description_lower for keyword in ['ethernet', 'gigabit', 'fast ethernet']):
            return AdapterType.ETHERNET
        else:
            return AdapterType.OTHER
    
    def get_adapter_by_id(self, adapter_id: str) -> Optional[NetworkAdapter]:
        """根据ID获取网络适配器"""
        try:
            adapters = self.get_network_adapters()
            for adapter in adapters:
                if adapter.id == adapter_id:
                    return adapter
            return None
            
        except Exception as e:
            self.logger.error(f"获取网络适配器失败: {e}")
            return None
    
    def get_current_mac_address(self, adapter_id: str) -> Optional[str]:
        """获取指定网卡的当前MAC地址"""
        try:
            adapter = self.get_adapter_by_id(adapter_id)
            if adapter:
                return adapter.mac_address
            return None
            
        except Exception as e:
            self.logger.error(f"获取MAC地址失败: {e}")
            return None
    
    def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
        """修改网卡MAC地址"""
        try:
            # 验证MAC地址格式
            if not self._validate_mac_address(new_mac):
                raise NetworkAdapterError(f"无效的MAC地址格式: {new_mac}")
            
            # 获取适配器信息
            adapter = self.get_adapter_by_id(adapter_id)
            if not adapter:
                raise NetworkAdapterError(f"找不到网络适配器: {adapter_id}")
            
            if not adapter.can_modify or not adapter.registry_path:
                raise NetworkAdapterError(f"网络适配器不支持MAC地址修改: {adapter.name}")
            
            # 格式化MAC地址（去掉冒号）
            formatted_mac = new_mac.replace(':', '').replace('-', '').upper()
            
            # 修改注册表
            self.registry_manager.write_value(
                adapter.registry_path,
                "NetworkAddress",
                formatted_mac,
                winreg.REG_SZ
            )
            
            # 重启网卡
            if self._restart_network_adapter(adapter.name):
                self.logger.info(f"MAC地址修改成功: {adapter.name} -> {new_mac}")
                return True
            else:
                self.logger.warning(f"MAC地址已修改，但网卡重启失败: {adapter.name}")
                return True  # 修改成功，但需要手动重启
                
        except Exception as e:
            self.logger.error(f"修改MAC地址失败: {e}")
            raise NetworkAdapterError(f"修改MAC地址失败: {e}")
    
    def restore_original_mac(self, adapter_id: str) -> bool:
        """恢复网卡原始MAC地址"""
        try:
            adapter = self.get_adapter_by_id(adapter_id)
            if not adapter or not adapter.registry_path:
                raise NetworkAdapterError(f"找不到网络适配器: {adapter_id}")
            
            # 删除NetworkAddress值以恢复原始MAC
            self.registry_manager.delete_value(
                adapter.registry_path,
                "NetworkAddress"
            )
            
            # 重启网卡
            if self._restart_network_adapter(adapter.name):
                self.logger.info(f"MAC地址已恢复原始值: {adapter.name}")
                return True
            else:
                self.logger.warning(f"MAC地址已恢复，但网卡重启失败: {adapter.name}")
                return True
                
        except Exception as e:
            self.logger.error(f"恢复MAC地址失败: {e}")
            raise NetworkAdapterError(f"恢复MAC地址失败: {e}")
    
    def _validate_mac_address(self, mac_address: str) -> bool:
        """验证MAC地址格式"""
        # 支持的格式: XX:XX:XX:XX:XX:XX 或 XX-XX-XX-XX-XX-XX
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac_address))
    
    def _restart_network_adapter(self, adapter_name: str) -> bool:
        """重启网络适配器"""
        try:
            # 禁用网卡
            disable_cmd = f'netsh interface set interface "{adapter_name}" admin=disable'
            result1 = subprocess.run(disable_cmd, shell=True, capture_output=True, text=True)
            
            # 启用网卡
            enable_cmd = f'netsh interface set interface "{adapter_name}" admin=enable'
            result2 = subprocess.run(enable_cmd, shell=True, capture_output=True, text=True)
            
            success = result1.returncode == 0 and result2.returncode == 0
            
            if success:
                self.logger.info(f"网卡重启成功: {adapter_name}")
            else:
                self.logger.warning(f"网卡重启失败: {adapter_name}")
                self.logger.debug(f"禁用结果: {result1.stderr}")
                self.logger.debug(f"启用结果: {result2.stderr}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"重启网卡失败: {e}")
            return False
    
    def generate_random_mac(self, vendor_prefix: str = None) -> str:
        """生成随机MAC地址"""
        import random
        
        if vendor_prefix:
            # 使用指定的厂商前缀
            prefix = vendor_prefix.replace(':', '').replace('-', '')[:6]
            if len(prefix) != 6:
                raise NetworkAdapterError("厂商前缀必须是3字节（6个十六进制字符）")
            
            # 生成后3字节
            suffix = ''.join([f'{random.randint(0, 255):02X}' for _ in range(3)])
            mac_hex = prefix + suffix
        else:
            # 生成完全随机的MAC地址
            # 第一个字节设置为本地管理地址（第二位设置为1）
            first_byte = random.randint(0, 255) | 0x02  # 设置本地管理位
            first_byte = first_byte & 0xFE  # 清除多播位
            
            mac_bytes = [first_byte] + [random.randint(0, 255) for _ in range(5)]
            mac_hex = ''.join([f'{b:02X}' for b in mac_bytes])
        
        # 格式化为标准MAC地址格式
        mac_formatted = ':'.join([mac_hex[i:i+2] for i in range(0, 12, 2)])
        
        self.logger.debug(f"生成随机MAC地址: {mac_formatted}")
        return mac_formatted

# 全局网络管理器实例
_network_manager: Optional[NetworkManager] = None

def get_network_manager() -> NetworkManager:
    """获取全局网络管理器实例"""
    global _network_manager
    if _network_manager is None:
        _network_manager = NetworkManager()
    return _network_manager
