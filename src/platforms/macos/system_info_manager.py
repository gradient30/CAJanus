#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS系统信息管理器
获取macOS系统和硬件信息，包括IORegistry信息
"""

import subprocess
import re
import json
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.logger import get_logger
from core.exceptions import OperationError

class SystemInfoManager:
    """macOS系统信息管理器"""
    
    def __init__(self):
        self.logger = get_logger("macos_system_info")
        self.logger.info("macOS系统信息管理器初始化完成")
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        try:
            system_info = {}
            
            # 获取系统版本信息
            result = subprocess.run(['sw_vers'], capture_output=True, text=True)
            if result.returncode == 0:
                version_info = {}
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        version_info[key.strip()] = value.strip()
                system_info['version'] = version_info
            
            # 获取系统启动时间
            try:
                result = subprocess.run(['uptime'], capture_output=True, text=True)
                if result.returncode == 0:
                    system_info['uptime'] = result.stdout.strip()
            except Exception as e:
                self.logger.warning(f"获取系统启动时间失败: {e}")
            
            # 获取内核信息
            try:
                result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
                if result.returncode == 0:
                    system_info['kernel'] = result.stdout.strip()
            except Exception as e:
                self.logger.warning(f"获取内核信息失败: {e}")
            
            self.logger.info("系统信息获取完成")
            return system_info
            
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            raise OperationError(f"获取系统信息失败: {e}")
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        try:
            hardware_info = {}
            
            # 获取硬件概览
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                hardware_data = self._parse_system_profiler_output(result.stdout)
                hardware_info['hardware_overview'] = hardware_data
            
            # 获取CPU信息
            try:
                cpu_info = self._get_cpu_info()
                hardware_info['cpu'] = cpu_info
            except Exception as e:
                self.logger.warning(f"获取CPU信息失败: {e}")
            
            # 获取内存信息
            try:
                memory_info = self._get_memory_info()
                hardware_info['memory'] = memory_info
            except Exception as e:
                self.logger.warning(f"获取内存信息失败: {e}")
            
            # 获取存储信息
            try:
                storage_info = self._get_storage_info()
                hardware_info['storage'] = storage_info
            except Exception as e:
                self.logger.warning(f"获取存储信息失败: {e}")
            
            self.logger.info("硬件信息获取完成")
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"获取硬件信息失败: {e}")
            return {}
    
    def _parse_system_profiler_output(self, output: str) -> Dict[str, str]:
        """解析system_profiler输出"""
        data = {}
        for line in output.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('System Information:'):
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return data
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        cpu_info = {}
        
        # 获取CPU品牌和型号
        try:
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                cpu_info['brand_string'] = result.stdout.strip()
        except Exception:
            pass
        
        # 获取CPU核心数
        try:
            result = subprocess.run(['sysctl', '-n', 'hw.ncpu'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                cpu_info['core_count'] = int(result.stdout.strip())
        except Exception:
            pass
        
        # 获取CPU频率
        try:
            result = subprocess.run(['sysctl', '-n', 'hw.cpufrequency'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                cpu_info['frequency'] = int(result.stdout.strip())
        except Exception:
            pass
        
        return cpu_info
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        memory_info = {}
        
        # 获取物理内存大小
        try:
            result = subprocess.run(['sysctl', '-n', 'hw.memsize'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                memory_info['physical_memory'] = int(result.stdout.strip())
        except Exception:
            pass
        
        # 获取内存使用情况
        try:
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            if result.returncode == 0:
                vm_stats = self._parse_vm_stat(result.stdout)
                memory_info['vm_stats'] = vm_stats
        except Exception:
            pass
        
        return memory_info
    
    def _parse_vm_stat(self, output: str) -> Dict[str, int]:
        """解析vm_stat输出"""
        stats = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().replace(' ', '_').lower()
                value = value.strip().rstrip('.')
                try:
                    stats[key] = int(value)
                except ValueError:
                    pass
        return stats
    
    def _get_storage_info(self) -> List[Dict[str, Any]]:
        """获取存储信息"""
        storage_info = []
        
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6 and parts[5].startswith('/'):
                        storage_info.append({
                            'filesystem': parts[0],
                            'size': parts[1],
                            'used': parts[2],
                            'available': parts[3],
                            'capacity': parts[4],
                            'mount_point': parts[5]
                        })
        except Exception as e:
            self.logger.warning(f"获取存储信息失败: {e}")
        
        return storage_info
    
    def get_ioreg_info(self) -> Dict[str, Any]:
        """获取IORegistry信息"""
        try:
            ioreg_info = {}
            
            # 获取IOPlatformExpertDevice信息
            result = subprocess.run(['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                platform_info = self._parse_ioreg_output(result.stdout)
                ioreg_info['platform'] = platform_info
            
            # 获取网络接口信息
            try:
                result = subprocess.run(['ioreg', '-c', 'IOEthernetInterface'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    network_info = self._parse_ioreg_output(result.stdout)
                    ioreg_info['network'] = network_info
            except Exception as e:
                self.logger.warning(f"获取网络接口IORegistry信息失败: {e}")
            
            self.logger.info("IORegistry信息获取完成")
            return ioreg_info
            
        except Exception as e:
            self.logger.error(f"获取IORegistry信息失败: {e}")
            return {}
    
    def _parse_ioreg_output(self, output: str) -> Dict[str, Any]:
        """解析ioreg输出"""
        info = {}
        
        # 提取IOPlatformUUID
        uuid_match = re.search(r'"IOPlatformUUID" = "([^"]+)"', output)
        if uuid_match:
            info['IOPlatformUUID'] = uuid_match.group(1)
        
        # 提取IOPlatformSerialNumber
        serial_match = re.search(r'"IOPlatformSerialNumber" = "([^"]+)"', output)
        if serial_match:
            info['IOPlatformSerialNumber'] = serial_match.group(1)
        
        # 提取其他有用信息
        for line in output.split('\n'):
            line = line.strip()
            if '"' in line and '=' in line:
                # 匹配格式: "key" = "value" 或 "key" = <value>
                match = re.match(r'"([^"]+)"\s*=\s*"([^"]*)"', line)
                if not match:
                    match = re.match(r'"([^"]+)"\s*=\s*<([^>]*)>', line)
                if not match:
                    match = re.match(r'"([^"]+)"\s*=\s*(\w+)', line)
                
                if match:
                    key, value = match.groups()
                    if key not in info:  # 避免重复
                        info[key] = value
        
        return info
    
    def get_hardware_uuid(self) -> Optional[str]:
        """获取硬件UUID"""
        try:
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Hardware UUID' in line:
                        uuid_match = re.search(r'Hardware UUID: ([A-F0-9-]+)', line)
                        if uuid_match:
                            return uuid_match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取硬件UUID失败: {e}")
            return None
    
    def get_platform_serial(self) -> Optional[str]:
        """获取平台序列号"""
        try:
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Serial Number' in line:
                        serial_match = re.search(r'Serial Number \(system\): (.+)', line)
                        if serial_match:
                            return serial_match.group(1).strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取平台序列号失败: {e}")
            return None
    
    def get_network_interfaces_info(self) -> List[Dict[str, Any]]:
        """获取网络接口详细信息"""
        try:
            interfaces = []
            
            # 获取网络接口列表
            result = subprocess.run(['networksetup', '-listallhardwareports'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                current_interface = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('Hardware Port:'):
                        if current_interface:
                            interfaces.append(current_interface)
                        current_interface = {'name': line.split(':', 1)[1].strip()}
                    elif line.startswith('Device:'):
                        current_interface['device'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Ethernet Address:'):
                        current_interface['mac_address'] = line.split(':', 1)[1].strip()
                
                if current_interface:
                    interfaces.append(current_interface)
            
            self.logger.info(f"获取到 {len(interfaces)} 个网络接口")
            return interfaces
            
        except Exception as e:
            self.logger.error(f"获取网络接口信息失败: {e}")
            return []
    
    def get_system_fingerprint(self) -> Dict[str, Any]:
        """获取完整的系统指纹信息"""
        try:
            fingerprint = {
                'system_info': self.get_system_info(),
                'hardware_info': self.get_hardware_info(),
                'ioreg_info': self.get_ioreg_info(),
                'hardware_uuid': self.get_hardware_uuid(),
                'platform_serial': self.get_platform_serial(),
                'network_interfaces': self.get_network_interfaces_info()
            }
            
            self.logger.info("系统指纹信息获取完成")
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"获取系统指纹失败: {e}")
            return {}

# 全局系统信息管理器实例
_system_info_manager = None

def get_system_info_manager() -> SystemInfoManager:
    """获取全局系统信息管理器实例"""
    global _system_info_manager
    if _system_info_manager is None:
        _system_info_manager = SystemInfoManager()
    return _system_info_manager
