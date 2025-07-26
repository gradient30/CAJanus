#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows WMI管理器
提供WMI接口封装，用于获取系统和硬件信息
"""

import subprocess
import json
import uuid
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.logger import get_logger
from core.exceptions import OperationError

class WMIManager:
    """Windows WMI管理器"""
    
    def __init__(self):
        self.logger = get_logger("wmi_manager")
        self.logger.info("WMI管理器初始化完成")
    
    def _execute_wmi_query(self, wmi_class: str, properties: List[str] = None, 
                          where_clause: str = None) -> List[Dict[str, Any]]:
        """执行WMI查询"""
        try:
            # 构建查询命令
            if properties:
                props = ','.join(properties)
            else:
                props = '*'
            
            cmd = f'wmic {wmi_class} get {props} /format:csv'
            if where_clause:
                cmd += f' where "{where_clause}"'
            
            self.logger.debug(f"执行WMI查询: {cmd}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True,
                                  text=True, encoding='gbk', errors='ignore')
            
            if result.returncode != 0:
                raise OperationError(f"WMI查询失败: {result.stderr}")
            
            # 解析CSV输出
            if not result.stdout:
                return []

            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []
            
            # 获取列标题
            headers = [h.strip() for h in lines[0].split(',')[1:]]  # 跳过第一列（Node）
            
            # 解析数据行
            data = []
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                values = [v.strip() for v in line.split(',')[1:]]  # 跳过第一列
                if len(values) == len(headers):
                    row = dict(zip(headers, values))
                    # 过滤空值
                    row = {k: v for k, v in row.items() if v}
                    if row:  # 只添加非空行
                        data.append(row)
            
            return data
            
        except Exception as e:
            self.logger.error(f"WMI查询执行失败: {e}")
            raise OperationError(f"WMI查询执行失败: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            # 获取计算机系统信息
            computer_system = self._execute_wmi_query(
                'computersystem',
                ['Name', 'Manufacturer', 'Model', 'TotalPhysicalMemory', 'NumberOfProcessors']
            )
            
            # 获取操作系统信息
            os_info = self._execute_wmi_query(
                'os',
                ['Caption', 'Version', 'BuildNumber', 'OSArchitecture', 'InstallDate']
            )
            
            # 获取BIOS信息
            bios_info = self._execute_wmi_query(
                'bios',
                ['Manufacturer', 'SMBIOSBIOSVersion', 'ReleaseDate']
            )
            
            system_info = {
                'computer_system': computer_system[0] if computer_system else {},
                'operating_system': os_info[0] if os_info else {},
                'bios': bios_info[0] if bios_info else {}
            }
            
            self.logger.info("系统信息获取完成")
            return system_info
            
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            raise OperationError(f"获取系统信息失败: {e}")
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        try:
            hardware_info = {}
            
            # 主板信息
            motherboard = self._execute_wmi_query(
                'baseboard',
                ['Manufacturer', 'Product', 'SerialNumber', 'Version']
            )
            hardware_info['motherboard'] = motherboard[0] if motherboard else {}
            
            # CPU信息
            processor = self._execute_wmi_query(
                'cpu',
                ['Name', 'Manufacturer', 'ProcessorId', 'MaxClockSpeed', 'NumberOfCores']
            )
            hardware_info['processor'] = processor[0] if processor else {}
            
            # 内存信息
            try:
                memory = self._execute_wmi_query(
                    'path win32_physicalmemory',
                    ['Capacity', 'Speed', 'Manufacturer', 'PartNumber']
                )
                hardware_info['memory'] = memory
            except Exception as e:
                self.logger.warning(f"获取内存信息失败: {e}")
                hardware_info['memory'] = []
            
            # 磁盘信息
            try:
                disks = self._execute_wmi_query(
                    'path win32_diskdrive',
                    ['Model', 'SerialNumber', 'Size', 'InterfaceType']
                )
                hardware_info['disks'] = disks
            except Exception as e:
                self.logger.warning(f"获取磁盘信息失败: {e}")
                hardware_info['disks'] = []
            
            self.logger.info("硬件信息获取完成")
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"获取硬件信息失败: {e}")
            raise OperationError(f"获取硬件信息失败: {e}")
    
    def get_network_adapters(self) -> List[Dict[str, Any]]:
        """获取网络适配器信息"""
        try:
            adapters = self._execute_wmi_query(
                'path win32_networkadapter',
                ['Name', 'MACAddress', 'PNPDeviceID', 'Description', 'NetEnabled', 'AdapterType']
            )
            
            # 过滤有效的网络适配器
            valid_adapters = []
            for adapter in adapters:
                if adapter.get('MACAddress') and len(adapter['MACAddress']) == 17:
                    valid_adapters.append(adapter)
            
            self.logger.info(f"获取到 {len(valid_adapters)} 个有效网络适配器")
            return valid_adapters
            
        except Exception as e:
            self.logger.error(f"获取网络适配器信息失败: {e}")
            raise OperationError(f"获取网络适配器信息失败: {e}")
    
    def get_logical_disks(self) -> List[Dict[str, Any]]:
        """获取逻辑磁盘信息"""
        try:
            disks = self._execute_wmi_query(
                'logicaldisk',
                ['DeviceID', 'Size', 'FreeSpace', 'VolumeSerialNumber', 'FileSystem', 'VolumeName']
            )
            
            self.logger.info(f"获取到 {len(disks)} 个逻辑磁盘")
            return disks
            
        except Exception as e:
            self.logger.error(f"获取逻辑磁盘信息失败: {e}")
            raise OperationError(f"获取逻辑磁盘信息失败: {e}")
    
    def get_machine_guid(self) -> Optional[str]:
        """获取机器GUID"""
        try:
            # 从注册表获取MachineGuid
            from .registry_manager import get_registry_manager
            registry_manager = get_registry_manager()
            
            guid = registry_manager.read_value(
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography",
                "MachineGuid"
            )
            
            if guid:
                self.logger.info(f"获取机器GUID: {guid}")
                return guid
            else:
                self.logger.warning("未找到机器GUID")
                return None
                
        except Exception as e:
            self.logger.error(f"获取机器GUID失败: {e}")
            return None
    
    def modify_machine_guid(self, new_guid: str = None) -> bool:
        """修改机器GUID"""
        try:
            if new_guid is None:
                new_guid = str(uuid.uuid4())
            
            # 验证GUID格式
            try:
                uuid.UUID(new_guid)
            except ValueError:
                raise OperationError(f"无效的GUID格式: {new_guid}")
            
            from .registry_manager import get_registry_manager
            registry_manager = get_registry_manager()
            
            # 修改注册表中的MachineGuid
            success = registry_manager.write_value(
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography",
                "MachineGuid",
                new_guid
            )
            
            if success:
                self.logger.info(f"机器GUID修改成功: {new_guid}")
                return True
            else:
                self.logger.error("机器GUID修改失败")
                return False
                
        except Exception as e:
            self.logger.error(f"修改机器GUID失败: {e}")
            raise OperationError(f"修改机器GUID失败: {e}")
    
    def get_volume_serial_numbers(self) -> Dict[str, str]:
        """获取磁盘卷序列号"""
        try:
            disks = self.get_logical_disks()
            serials = {}
            
            for disk in disks:
                device_id = disk.get('DeviceID', '')
                serial = disk.get('VolumeSerialNumber', '')
                if device_id and serial:
                    serials[device_id] = serial
            
            self.logger.info(f"获取到 {len(serials)} 个磁盘卷序列号")
            return serials
            
        except Exception as e:
            self.logger.error(f"获取磁盘卷序列号失败: {e}")
            return {}
    
    def get_installed_software(self) -> List[Dict[str, Any]]:
        """获取已安装软件列表"""
        try:
            software = self._execute_wmi_query(
                'product',
                ['Name', 'Version', 'Vendor', 'InstallDate']
            )
            
            self.logger.info(f"获取到 {len(software)} 个已安装软件")
            return software
            
        except Exception as e:
            self.logger.error(f"获取已安装软件失败: {e}")
            return []
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """获取运行中的进程"""
        try:
            processes = self._execute_wmi_query(
                'process',
                ['Name', 'ProcessId', 'ExecutablePath', 'CommandLine', 'WorkingSetSize']
            )
            
            self.logger.info(f"获取到 {len(processes)} 个运行进程")
            return processes
            
        except Exception as e:
            self.logger.error(f"获取运行进程失败: {e}")
            return []
    
    def get_services(self) -> List[Dict[str, Any]]:
        """获取系统服务"""
        try:
            services = self._execute_wmi_query(
                'service',
                ['Name', 'DisplayName', 'State', 'StartMode', 'PathName']
            )
            
            self.logger.info(f"获取到 {len(services)} 个系统服务")
            return services
            
        except Exception as e:
            self.logger.error(f"获取系统服务失败: {e}")
            return []
    
    def get_startup_programs(self) -> List[Dict[str, Any]]:
        """获取启动程序"""
        try:
            startup = self._execute_wmi_query(
                'startup',
                ['Name', 'Command', 'Location', 'User']
            )
            
            self.logger.info(f"获取到 {len(startup)} 个启动程序")
            return startup
            
        except Exception as e:
            self.logger.error(f"获取启动程序失败: {e}")
            return []

# 全局WMI管理器实例
_wmi_manager: Optional[WMIManager] = None

def get_wmi_manager() -> WMIManager:
    """获取全局WMI管理器实例"""
    global _wmi_manager
    if _wmi_manager is None:
        _wmi_manager = WMIManager()
    return _wmi_manager
