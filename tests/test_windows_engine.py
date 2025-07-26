#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows平台引擎测试脚本
测试注册表管理、网络管理、WMI接口和设备指纹管理功能
"""

import sys
import os
import platform as platform_module
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_registry_manager():
    """测试注册表管理器"""
    print("=== 测试注册表管理器 ===")
    
    if platform_module.system() != 'Windows':
        print("⏭️  跳过注册表管理器测试（非Windows平台）")
        return True
    
    try:
        from platforms.windows.registry_manager import get_registry_manager
        
        registry_manager = get_registry_manager()
        
        # 测试读取注册表值
        test_path = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        program_files = registry_manager.read_value(test_path, "ProgramFilesDir")
        print(f"程序文件目录: {program_files}")
        
        # 测试枚举注册表值
        values = registry_manager.enumerate_values(test_path)
        print(f"找到 {len(values)} 个注册表值")
        
        # 测试备份功能
        backup_id = registry_manager.backup_registry_key(test_path)
        print(f"备份ID: {backup_id}")
        
        # 测试列出备份
        backups = registry_manager.list_backups()
        print(f"备份数量: {len(backups)}")
        
        print("✅ 注册表管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 注册表管理器测试失败: {e}")
        return False

def test_network_manager():
    """测试网络管理器"""
    print("\n=== 测试网络管理器 ===")
    
    if platform_module.system() != 'Windows':
        print("⏭️  跳过网络管理器测试（非Windows平台）")
        return True
    
    try:
        from platforms.windows.network_manager import get_network_manager
        
        network_manager = get_network_manager()
        
        # 测试获取网络适配器
        adapters = network_manager.get_network_adapters()
        print(f"找到 {len(adapters)} 个网络适配器")
        
        # 显示前3个适配器的信息
        for i, adapter in enumerate(adapters[:3]):
            print(f"  适配器 {i+1}: {adapter.name}")
            print(f"    MAC地址: {adapter.mac_address}")
            print(f"    类型: {adapter.adapter_type.value}")
            print(f"    可修改: {adapter.can_modify}")
        
        # 测试生成随机MAC地址
        random_mac = network_manager.generate_random_mac()
        print(f"随机MAC地址: {random_mac}")
        
        # 测试MAC地址验证
        valid_mac = network_manager._validate_mac_address("00:11:22:33:44:55")
        invalid_mac = network_manager._validate_mac_address("invalid")
        print(f"MAC地址验证: 有效={valid_mac}, 无效={not invalid_mac}")
        
        print("✅ 网络管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 网络管理器测试失败: {e}")
        return False

def test_wmi_manager():
    """测试WMI管理器"""
    print("\n=== 测试WMI管理器 ===")
    
    if platform_module.system() != 'Windows':
        print("⏭️  跳过WMI管理器测试（非Windows平台）")
        return True
    
    try:
        from platforms.windows.wmi_manager import get_wmi_manager
        
        wmi_manager = get_wmi_manager()
        
        # 测试获取系统信息
        system_info = wmi_manager.get_system_info()
        print(f"计算机名: {system_info.get('computer_system', {}).get('Name', 'Unknown')}")
        print(f"操作系统: {system_info.get('operating_system', {}).get('Caption', 'Unknown')}")
        
        # 测试获取硬件信息
        hardware_info = wmi_manager.get_hardware_info()
        cpu_name = hardware_info.get('processor', {}).get('Name', 'Unknown')
        print(f"处理器: {cpu_name}")
        
        # 测试获取机器GUID
        machine_guid = wmi_manager.get_machine_guid()
        print(f"机器GUID: {machine_guid}")
        
        # 测试获取磁盘卷序列号
        volume_serials = wmi_manager.get_volume_serial_numbers()
        print(f"磁盘卷序列号: {volume_serials}")
        
        # 测试获取网络适配器
        network_adapters = wmi_manager.get_network_adapters()
        print(f"WMI网络适配器数量: {len(network_adapters)}")
        
        print("✅ WMI管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ WMI管理器测试失败: {e}")
        return False

def test_fingerprint_manager():
    """测试设备指纹管理器"""
    print("\n=== 测试设备指纹管理器 ===")
    
    if platform_module.system() != 'Windows':
        print("⏭️  跳过设备指纹管理器测试（非Windows平台）")
        return True
    
    try:
        from platforms.windows.fingerprint_manager import get_windows_fingerprint_manager
        
        fingerprint_manager = get_windows_fingerprint_manager()
        
        # 测试获取网络适配器
        adapters = fingerprint_manager.get_network_adapters()
        print(f"网络适配器数量: {len(adapters)}")
        
        # 测试获取机器GUID
        machine_guid = fingerprint_manager.get_machine_guid()
        print(f"机器GUID: {machine_guid}")
        
        # 测试获取卷序列号
        volume_serials = fingerprint_manager.get_volume_serial_numbers()
        print(f"卷序列号: {list(volume_serials.keys())}")
        
        # 测试获取硬件信息
        hardware_info = fingerprint_manager.get_hardware_info()
        print(f"硬件信息类别: {list(hardware_info.keys())}")
        
        # 测试获取完整系统指纹
        fingerprint = fingerprint_manager.get_system_fingerprint()
        print(f"系统指纹包含: {list(fingerprint.keys())}")
        
        # 测试生成随机MAC地址
        random_mac = fingerprint_manager.generate_random_mac()
        print(f"随机MAC地址: {random_mac}")
        
        # 测试验证指纹修改
        test_changes = {
            'mac_changes': {
                'test_adapter': '00:11:22:33:44:55'
            }
        }
        validation = fingerprint_manager.validate_fingerprint_changes(test_changes)
        print(f"指纹修改验证: 有效={validation['valid']}, 风险等级={validation['risk_level']}")
        
        print("✅ 设备指纹管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 设备指纹管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_permission_integration():
    """测试权限集成"""
    print("\n=== 测试权限集成 ===")
    
    if platform_module.system() != 'Windows':
        print("⏭️  跳过权限集成测试（非Windows平台）")
        return True
    
    try:
        from platforms.windows.permission_manager import WindowsPermissionManager
        
        perm_manager = WindowsPermissionManager()
        
        # 测试各种操作的权限要求
        operations = [
            'modify_mac_address',
            'modify_machine_guid',
            'modify_volume_serial',
            'delete_file'
        ]
        
        for operation in operations:
            required_perms = perm_manager.get_required_permissions(operation)
            has_perms = perm_manager.validate_permissions_for_operation(operation)
            print(f"操作 {operation}: 需要权限={required_perms}, 具备权限={has_perms}")
        
        # 测试权限信息
        perm_info = perm_manager.get_permission_info()
        print(f"权限信息: {perm_info}")
        
        print("✅ 权限集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 权限集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始Windows平台引擎测试...\n")
    
    if platform_module.system() != 'Windows':
        print("⚠️  当前不是Windows平台，将跳过大部分测试")
    
    test_functions = [
        test_registry_manager,
        test_network_manager,
        test_wmi_manager,
        test_fingerprint_manager,
        test_permission_integration
    ]
    
    results = []
    for test_func in test_functions:
        results.append(test_func())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！Windows平台引擎功能正常")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
