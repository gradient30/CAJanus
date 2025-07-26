#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS平台引擎测试脚本
测试macOS平台的权限管理、系统信息、网络管理和设备指纹管理功能
"""

import sys
import os
import platform as platform_module
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_macos_permission_manager():
    """测试macOS权限管理器"""
    print("=== 测试macOS权限管理器 ===")
    
    if platform_module.system() != 'Darwin':
        print("⏭️  跳过macOS权限管理器测试（非macOS平台）")
        return True
    
    try:
        from platforms.macos.permission_manager import get_macos_permission_manager
        
        perm_manager = get_macos_permission_manager()
        
        # 测试权限检查
        is_root = perm_manager.check_admin_privileges()
        has_sudo = perm_manager.check_sudo_privileges()
        current_user = perm_manager.get_current_user()
        
        print(f"Root权限: {is_root}")
        print(f"Sudo权限: {has_sudo}")
        print(f"当前用户: {current_user}")
        
        # 测试SIP状态
        sip_status = perm_manager.check_sip_status()
        print(f"SIP状态: {sip_status}")
        
        # 测试权限信息
        perm_info = perm_manager.get_permission_info()
        print(f"权限信息: {perm_info}")
        
        # 测试用户组
        user_groups = perm_manager.get_user_groups()
        is_admin = perm_manager.is_in_admin_group()
        print(f"用户组: {user_groups}")
        print(f"Admin组成员: {is_admin}")
        
        print("✅ macOS权限管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ macOS权限管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_macos_system_info_manager():
    """测试macOS系统信息管理器"""
    print("\n=== 测试macOS系统信息管理器 ===")
    
    if platform_module.system() != 'Darwin':
        print("⏭️  跳过macOS系统信息管理器测试（非macOS平台）")
        return True
    
    try:
        from platforms.macos.system_info_manager import get_system_info_manager
        
        system_manager = get_system_info_manager()
        
        # 测试获取系统信息
        system_info = system_manager.get_system_info()
        print(f"系统信息类别: {list(system_info.keys())}")
        
        # 测试获取硬件信息
        hardware_info = system_manager.get_hardware_info()
        print(f"硬件信息类别: {list(hardware_info.keys())}")
        
        # 测试获取IORegistry信息
        ioreg_info = system_manager.get_ioreg_info()
        print(f"IORegistry信息: {list(ioreg_info.keys())}")
        
        # 测试获取硬件UUID
        hardware_uuid = system_manager.get_hardware_uuid()
        print(f"硬件UUID: {hardware_uuid}")
        
        # 测试获取平台序列号
        platform_serial = system_manager.get_platform_serial()
        print(f"平台序列号: {platform_serial}")
        
        # 测试获取网络接口信息
        network_interfaces = system_manager.get_network_interfaces_info()
        print(f"网络接口数量: {len(network_interfaces)}")
        
        print("✅ macOS系统信息管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ macOS系统信息管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_macos_network_manager():
    """测试macOS网络管理器"""
    print("\n=== 测试macOS网络管理器 ===")
    
    if platform_module.system() != 'Darwin':
        print("⏭️  跳过macOS网络管理器测试（非macOS平台）")
        return True
    
    try:
        from platforms.macos.network_manager import get_macos_network_manager
        
        network_manager = get_macos_network_manager()
        
        # 测试获取网络适配器
        adapters = network_manager.get_network_adapters()
        print(f"找到 {len(adapters)} 个网络适配器")
        
        # 显示前3个适配器的信息
        for i, adapter in enumerate(adapters[:3]):
            print(f"  适配器 {i+1}: {adapter.name}")
            print(f"    接口名: {adapter.interface_name}")
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
        
        print("✅ macOS网络管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ macOS网络管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_macos_fingerprint_manager():
    """测试macOS设备指纹管理器"""
    print("\n=== 测试macOS设备指纹管理器 ===")
    
    if platform_module.system() != 'Darwin':
        print("⏭️  跳过macOS设备指纹管理器测试（非macOS平台）")
        return True
    
    try:
        from platforms.macos.fingerprint_manager import get_macos_fingerprint_manager
        
        fingerprint_manager = get_macos_fingerprint_manager()
        
        # 测试获取网络适配器
        adapters = fingerprint_manager.get_network_adapters()
        print(f"网络适配器数量: {len(adapters)}")
        
        # 测试获取硬件UUID
        hardware_uuid = fingerprint_manager.get_machine_guid()
        print(f"硬件UUID: {hardware_uuid}")
        
        # 测试获取卷信息
        volume_info = fingerprint_manager.get_volume_serial_numbers()
        print(f"卷信息: {list(volume_info.keys())}")
        
        # 测试获取硬件信息
        hardware_info = fingerprint_manager.get_hardware_info()
        print(f"硬件信息类别: {list(hardware_info.keys())}")
        
        # 测试获取完整系统指纹
        fingerprint = fingerprint_manager.get_system_fingerprint()
        print(f"系统指纹包含: {list(fingerprint.keys())}")
        
        # 测试生成随机MAC地址
        random_mac = fingerprint_manager.generate_random_mac()
        print(f"随机MAC地址: {random_mac}")
        
        # 测试支持的操作
        supported_ops = fingerprint_manager.get_supported_operations()
        unsupported_ops = fingerprint_manager.get_unsupported_operations()
        print(f"支持的操作数量: {len(supported_ops)}")
        print(f"不支持的操作: {unsupported_ops}")
        
        # 测试验证指纹修改
        test_changes = {
            'mac_changes': {
                'en0': '00:11:22:33:44:55'
            }
        }
        validation = fingerprint_manager.validate_fingerprint_changes(test_changes)
        print(f"指纹修改验证: 有效={validation['valid']}, 风险等级={validation['risk_level']}")
        
        print("✅ macOS设备指纹管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ macOS设备指纹管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_structure():
    """测试代码结构（在非macOS平台上也能运行）"""
    print("\n=== 测试代码结构 ===")
    
    try:
        # 测试导入
        from platforms.macos.permission_manager import MacOSPermissionManager
        from platforms.macos.system_info_manager import SystemInfoManager
        from platforms.macos.network_manager import MacOSNetworkManager
        from platforms.macos.fingerprint_manager import MacOSFingerprintManager
        
        print("✅ 所有macOS模块导入成功")
        
        # 测试类实例化（不执行实际操作）
        if platform_module.system() != 'Darwin':
            print("⏭️  跳过实例化测试（非macOS平台）")
            return True
        
        # 在macOS平台上测试实例化
        perm_manager = MacOSPermissionManager()
        system_manager = SystemInfoManager()
        network_manager = MacOSNetworkManager()
        fingerprint_manager = MacOSFingerprintManager()
        
        print("✅ 所有macOS管理器实例化成功")
        return True
        
    except Exception as e:
        print(f"❌ 代码结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始macOS平台引擎测试...\n")
    
    current_platform = platform_module.system()
    print(f"当前平台: {current_platform}")
    
    if current_platform != 'Darwin':
        print("⚠️  当前不是macOS平台，将只测试代码结构")
    
    test_functions = [
        test_code_structure,
        test_macos_permission_manager,
        test_macos_system_info_manager,
        test_macos_network_manager,
        test_macos_fingerprint_manager
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
        if current_platform == 'Darwin':
            print("🎉 所有测试通过！macOS平台引擎功能正常")
        else:
            print("🎉 代码结构测试通过！macOS平台引擎代码结构正确")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
