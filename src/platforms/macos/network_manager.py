#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS网络管理器
处理macOS平台的网络接口管理和MAC地址修改
"""

import subprocess
import re
import time
from typing import List, Dict, Optional, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.interfaces import NetworkAdapter, AdapterType
from core.logger import get_logger
from core.exceptions import NetworkAdapterError
from .permission_manager import get_macos_permission_manager

class MacOSNetworkManager:
    """macOS网络管理器"""
    
    def __init__(self):
        self.logger = get_logger("macos_network")
        self.permission_manager = get_macos_permission_manager()
        self.logger.info("macOS网络管理器初始化完成")
    
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """获取所有网络适配器信息"""
        try:
            adapters = []
            
            # 获取ifconfig信息
            ifconfig_adapters = self._get_ifconfig_adapters()
            
            # 获取networksetup信息
            networksetup_adapters = self._get_networksetup_adapters()
            
            # 合并信息
            for ifconfig_adapter in ifconfig_adapters:
                # 查找对应的networksetup信息
                networksetup_info = None
                for ns_adapter in networksetup_adapters:
                    if (ifconfig_adapter.get('interface') == ns_adapter.get('device') or
                        ifconfig_adapter.get('mac_address') == ns_adapter.get('mac_address')):
                        networksetup_info = ns_adapter
                        break
                
                adapter = NetworkAdapter(
                    id=ifconfig_adapter.get('interface', ''),
                    name=networksetup_info.get('name', ifconfig_adapter.get('interface', '')),
                    description=ifconfig_adapter.get('description', ''),
                    mac_address=ifconfig_adapter.get('mac_address', ''),
                    status=ifconfig_adapter.get('status', 'unknown'),
                    adapter_type=self._determine_adapter_type(ifconfig_adapter.get('interface', '')),
                    can_modify=ifconfig_adapter.get('mac_address') is not None,
                    interface_name=ifconfig_adapter.get('interface')
                )
                
                adapters.append(adapter)
            
            self.logger.info(f"获取到 {len(adapters)} 个网络适配器")
            return adapters
            
        except Exception as e:
            self.logger.error(f"获取网络适配器失败: {e}")
            raise NetworkAdapterError(f"获取网络适配器失败: {e}")
    
    def _get_ifconfig_adapters(self) -> List[Dict[str, Any]]:
        """通过ifconfig获取网络接口信息"""
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise NetworkAdapterError(f"ifconfig命令执行失败: {result.stderr}")
            
            adapters = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                # 检查是否是新的接口
                if line and not line.startswith('\t') and not line.startswith(' '):
                    if current_interface:
                        adapters.append(current_interface)
                    
                    interface_name = line.split(':')[0]
                    current_interface = {
                        'interface': interface_name,
                        'mac_address': None,
                        'status': 'unknown',
                        'description': f'Network Interface {interface_name}'
                    }
                
                # 解析MAC地址
                elif current_interface and 'ether' in line:
                    mac_match = re.search(r'ether ([a-fA-F0-9:]{17})', line)
                    if mac_match:
                        current_interface['mac_address'] = mac_match.group(1)
                
                # 解析状态
                elif current_interface and 'status:' in line:
                    status_match = re.search(r'status: (\w+)', line)
                    if status_match:
                        current_interface['status'] = status_match.group(1)
                
                # 解析IP地址
                elif current_interface and 'inet ' in line:
                    ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        current_interface['ip_address'] = ip_match.group(1)
            
            # 添加最后一个接口
            if current_interface:
                adapters.append(current_interface)
            
            # 过滤掉没有MAC地址的接口（如lo0）
            valid_adapters = [adapter for adapter in adapters if adapter.get('mac_address')]
            
            return valid_adapters
            
        except Exception as e:
            self.logger.error(f"ifconfig获取网络接口信息失败: {e}")
            return []
    
    def _get_networksetup_adapters(self) -> List[Dict[str, Any]]:
        """通过networksetup获取网络接口信息"""
        try:
            result = subprocess.run(['networksetup', '-listallhardwareports'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.warning(f"networksetup命令执行失败: {result.stderr}")
                return []
            
            adapters = []
            current_adapter = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Hardware Port:'):
                    if current_adapter:
                        adapters.append(current_adapter)
                    current_adapter = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('Device:'):
                    current_adapter['device'] = line.split(':', 1)[1].strip()
                elif line.startswith('Ethernet Address:'):
                    current_adapter['mac_address'] = line.split(':', 1)[1].strip()
            
            if current_adapter:
                adapters.append(current_adapter)
            
            return adapters
            
        except Exception as e:
            self.logger.warning(f"networksetup获取网络接口信息失败: {e}")
            return []
    
    def _determine_adapter_type(self, interface_name: str) -> AdapterType:
        """根据接口名判断网卡类型"""
        interface_lower = interface_name.lower()
        
        if interface_lower.startswith('en'):
            # en0, en1 通常是以太网接口
            return AdapterType.ETHERNET
        elif interface_lower.startswith('wi') or interface_lower.startswith('wl'):
            # Wi-Fi接口
            return AdapterType.WIRELESS
        elif interface_lower.startswith('bt') or 'bluetooth' in interface_lower:
            # 蓝牙接口
            return AdapterType.BLUETOOTH
        elif any(keyword in interface_lower for keyword in ['vmnet', 'vnic', 'utun']):
            # 虚拟接口
            return AdapterType.VIRTUAL
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
            
            if not adapter.can_modify:
                raise NetworkAdapterError(f"网络适配器不支持MAC地址修改: {adapter.name}")
            
            # 检查权限
            if not self.permission_manager.validate_permissions_for_operation('modify_mac_address'):
                raise NetworkAdapterError("修改MAC地址需要sudo权限")
            
            interface_name = adapter.interface_name or adapter.id
            
            # 使用ifconfig修改MAC地址
            success, stdout, stderr = self.permission_manager.run_with_sudo(
                f'ifconfig {interface_name} ether {new_mac}'
            )
            
            if success:
                self.logger.info(f"MAC地址修改成功: {interface_name} -> {new_mac}")
                
                # 等待一下让系统更新
                time.sleep(1)
                
                # 验证修改是否成功
                current_mac = self.get_current_mac_address(adapter_id)
                if current_mac and current_mac.lower() == new_mac.lower():
                    return True
                else:
                    self.logger.warning(f"MAC地址修改可能未生效，当前MAC: {current_mac}")
                    return True  # 命令执行成功，但可能需要重启网卡
            else:
                self.logger.error(f"MAC地址修改失败: {stderr}")
                raise NetworkAdapterError(f"MAC地址修改失败: {stderr}")
                
        except Exception as e:
            self.logger.error(f"修改MAC地址失败: {e}")
            raise NetworkAdapterError(f"修改MAC地址失败: {e}")
    
    def restore_original_mac(self, adapter_id: str) -> bool:
        """恢复网卡原始MAC地址"""
        try:
            # 在macOS上，重启网络服务通常会恢复原始MAC地址
            adapter = self.get_adapter_by_id(adapter_id)
            if not adapter:
                raise NetworkAdapterError(f"找不到网络适配器: {adapter_id}")
            
            interface_name = adapter.interface_name or adapter.id
            
            # 尝试重启网络接口
            success = self._restart_network_interface(interface_name)
            
            if success:
                self.logger.info(f"网络接口重启成功，MAC地址应已恢复: {interface_name}")
                return True
            else:
                self.logger.warning(f"网络接口重启失败: {interface_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"恢复MAC地址失败: {e}")
            raise NetworkAdapterError(f"恢复MAC地址失败: {e}")
    
    def _restart_network_interface(self, interface_name: str) -> bool:
        """重启网络接口"""
        try:
            # 先关闭接口
            success1, _, stderr1 = self.permission_manager.run_with_sudo(
                f'ifconfig {interface_name} down'
            )
            
            if not success1:
                self.logger.warning(f"关闭网络接口失败: {stderr1}")
            
            # 等待一下
            time.sleep(2)
            
            # 再启用接口
            success2, _, stderr2 = self.permission_manager.run_with_sudo(
                f'ifconfig {interface_name} up'
            )
            
            if success2:
                self.logger.info(f"网络接口重启成功: {interface_name}")
                return True
            else:
                self.logger.error(f"启用网络接口失败: {stderr2}")
                return False
                
        except Exception as e:
            self.logger.error(f"重启网络接口失败: {e}")
            return False
    
    def _validate_mac_address(self, mac_address: str) -> bool:
        """验证MAC地址格式"""
        # 支持的格式: XX:XX:XX:XX:XX:XX 或 XX-XX-XX-XX-XX-XX
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac_address))
    
    def generate_random_mac(self, vendor_prefix: str = None) -> str:
        """生成随机MAC地址"""
        import random
        
        if vendor_prefix:
            # 使用指定的厂商前缀
            prefix = vendor_prefix.replace(':', '').replace('-', '')[:6]
            if len(prefix) != 6:
                raise NetworkAdapterError("厂商前缀必须是3字节（6个十六进制字符）")
            
            # 生成后3字节
            suffix = ''.join([f'{random.randint(0, 255):02x}' for _ in range(3)])
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
    
    def get_interface_statistics(self, interface_name: str) -> Dict[str, Any]:
        """获取网络接口统计信息"""
        try:
            result = subprocess.run(['netstat', '-i'], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {}
            
            stats = {}
            for line in result.stdout.split('\n')[1:]:  # 跳过标题行
                parts = line.split()
                if len(parts) >= 8 and parts[0] == interface_name:
                    stats = {
                        'packets_in': parts[4],
                        'errors_in': parts[5],
                        'packets_out': parts[6],
                        'errors_out': parts[7]
                    }
                    break
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取接口统计信息失败: {e}")
            return {}
    
    def get_active_connections(self) -> List[Dict[str, Any]]:
        """获取活跃的网络连接"""
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            connections = []
            for line in result.stdout.split('\n'):
                if 'ESTABLISHED' in line or 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        connections.append({
                            'protocol': parts[0],
                            'local_address': parts[3],
                            'foreign_address': parts[4],
                            'state': parts[5]
                        })
            
            return connections
            
        except Exception as e:
            self.logger.error(f"获取活跃连接失败: {e}")
            return []

# 全局macOS网络管理器实例
_macos_network_manager = None

def get_macos_network_manager() -> MacOSNetworkManager:
    """获取全局macOS网络管理器实例"""
    global _macos_network_manager
    if _macos_network_manager is None:
        _macos_network_manager = MacOSNetworkManager()
    return _macos_network_manager
