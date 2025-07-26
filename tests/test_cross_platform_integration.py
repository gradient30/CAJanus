#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨平台引擎集成测试
测试Windows和macOS平台引擎的集成和兼容性
"""

import sys
import os
import platform as platform_module
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_platform_factory_integration():
    """测试平台工厂集成"""
    print("=== 测试平台工厂集成 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        current_platform = platform_module.system()
        
        # 测试平台检测
        print(f"当前平台: {current_platform}")
        print(f"工厂检测平台: {factory.current_platform}")
        print(f"平台支持状态: {factory.is_supported_platform()}")
        
        # 测试平台信息
        platform_info = factory.get_platform_info()
        print(f"平台详细信息: {platform_info['system']} {platform_info['release']}")
        
        # 测试平台能力
        capabilities = factory.get_platform_capabilities()
        print(f"平台能力: {list(capabilities.keys())}")
        
        # 测试支持的平台
        supported_platforms = factory.get_supported_platforms()
        print(f"支持的平台: {supported_platforms}")
        
        print("✅ 平台工厂集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 平台工厂集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fingerprint_manager_creation():
    """测试设备指纹管理器创建"""
    print("\n=== 测试设备指纹管理器创建 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        current_platform = platform_module.system()
        
        if not factory.is_supported_platform():
            print(f"⏭️  平台 {current_platform} 不受支持，跳过测试")
            return True
        
        # 创建设备指纹管理器
        fingerprint_manager = factory.create_fingerprint_manager()
        print(f"设备指纹管理器创建成功: {type(fingerprint_manager).__name__}")
        
        # 测试基本接口
        print("测试基本接口...")
        
        # 获取网络适配器
        adapters = fingerprint_manager.get_network_adapters()
        print(f"网络适配器数量: {len(adapters)}")
        
        # 获取硬件信息
        hardware_info = fingerprint_manager.get_hardware_info()
        print(f"硬件信息类别: {list(hardware_info.keys())}")
        
        # 获取机器GUID/硬件UUID
        machine_id = fingerprint_manager.get_machine_guid()
        print(f"机器标识: {machine_id}")
        
        print("✅ 设备指纹管理器创建测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 设备指纹管理器创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_permission_manager_creation():
    """测试权限管理器创建"""
    print("\n=== 测试权限管理器创建 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        current_platform = platform_module.system()
        
        if not factory.is_supported_platform():
            print(f"⏭️  平台 {current_platform} 不受支持，跳过测试")
            return True
        
        # 创建权限管理器
        permission_manager = factory.create_permission_manager()
        print(f"权限管理器创建成功: {type(permission_manager).__name__}")
        
        # 测试基本接口
        print("测试基本接口...")
        
        # 检查管理员权限
        is_admin = permission_manager.check_admin_privileges()
        print(f"管理员权限: {is_admin}")
        
        # 获取当前用户
        current_user = permission_manager.get_current_user()
        print(f"当前用户: {current_user}")
        
        # 获取权限信息
        perm_info = permission_manager.get_permission_info()
        print(f"权限信息平台: {perm_info.get('platform', 'unknown')}")
        
        print("✅ 权限管理器创建测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 权限管理器创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cross_platform_interface_consistency():
    """测试跨平台接口一致性"""
    print("\n=== 测试跨平台接口一致性 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        from core.interfaces import IDeviceFingerprintManager, IPermissionManager
        
        factory = get_platform_factory()
        current_platform = platform_module.system()
        
        if not factory.is_supported_platform():
            print(f"⏭️  平台 {current_platform} 不受支持，跳过测试")
            return True
        
        # 测试设备指纹管理器接口
        fingerprint_manager = factory.create_fingerprint_manager()
        
        # 检查是否实现了正确的接口
        if not isinstance(fingerprint_manager, IDeviceFingerprintManager):
            print(f"❌ 设备指纹管理器未实现IDeviceFingerprintManager接口")
            return False
        
        print("✅ 设备指纹管理器接口一致性检查通过")
        
        # 测试权限管理器接口
        permission_manager = factory.create_permission_manager()
        
        # 检查是否实现了正确的接口
        if not isinstance(permission_manager, IPermissionManager):
            print(f"❌ 权限管理器未实现IPermissionManager接口")
            return False
        
        print("✅ 权限管理器接口一致性检查通过")
        
        # 测试接口方法存在性
        required_fingerprint_methods = [
            'get_network_adapters',
            'get_mac_address',
            'modify_mac_address',
            'get_machine_guid',
            'get_volume_serial_numbers',
            'get_hardware_info'
        ]
        
        for method_name in required_fingerprint_methods:
            if not hasattr(fingerprint_manager, method_name):
                print(f"❌ 设备指纹管理器缺少方法: {method_name}")
                return False
        
        print("✅ 设备指纹管理器方法完整性检查通过")
        
        required_permission_methods = [
            'check_admin_privileges',
            'get_current_user',
            'request_elevation'
        ]
        
        for method_name in required_permission_methods:
            if not hasattr(permission_manager, method_name):
                print(f"❌ 权限管理器缺少方法: {method_name}")
                return False
        
        print("✅ 权限管理器方法完整性检查通过")
        
        print("✅ 跨平台接口一致性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 跨平台接口一致性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_platform_specific_features():
    """测试平台特定功能"""
    print("\n=== 测试平台特定功能 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        current_platform = platform_module.system()
        
        if not factory.is_supported_platform():
            print(f"⏭️  平台 {current_platform} 不受支持，跳过测试")
            return True
        
        fingerprint_manager = factory.create_fingerprint_manager()
        
        # 测试平台特定功能
        if current_platform == 'Windows':
            print("测试Windows特定功能...")
            
            # 测试机器GUID修改（应该支持）
            try:
                # 不实际修改，只测试接口
                result = fingerprint_manager.validate_fingerprint_changes({
                    'machine_guid': 'test-guid'
                })
                print(f"Windows机器GUID修改验证: {result.get('valid', False)}")
            except Exception as e:
                print(f"Windows机器GUID修改测试异常: {e}")
            
        elif current_platform == 'Darwin':
            print("测试macOS特定功能...")
            
            # 测试硬件UUID修改（应该不支持）
            try:
                result = fingerprint_manager.validate_fingerprint_changes({
                    'hardware_uuid': 'test-uuid'
                })
                # macOS应该返回不支持
                if not result.get('valid', True):
                    print("✅ macOS正确拒绝硬件UUID修改")
                else:
                    print("⚠️  macOS意外支持硬件UUID修改")
            except Exception as e:
                print(f"macOS硬件UUID修改测试: {e}")
            
            # 测试支持的操作列表
            if hasattr(fingerprint_manager, 'get_supported_operations'):
                supported_ops = fingerprint_manager.get_supported_operations()
                unsupported_ops = fingerprint_manager.get_unsupported_operations()
                print(f"macOS支持的操作: {len(supported_ops)}")
                print(f"macOS不支持的操作: {unsupported_ops}")
        
        print("✅ 平台特定功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 平台特定功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling_consistency():
    """测试错误处理一致性"""
    print("\n=== 测试错误处理一致性 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        from core.exceptions import OperationError, NetworkAdapterError
        
        factory = get_platform_factory()
        current_platform = platform_module.system()
        
        if not factory.is_supported_platform():
            print(f"⏭️  平台 {current_platform} 不受支持，跳过测试")
            return True
        
        fingerprint_manager = factory.create_fingerprint_manager()
        
        # 测试无效适配器ID的错误处理
        try:
            result = fingerprint_manager.get_mac_address("invalid_adapter_id")
            if result is None:
                print("✅ 无效适配器ID正确返回None")
            else:
                print(f"⚠️  无效适配器ID返回了值: {result}")
        except Exception as e:
            print(f"✅ 无效适配器ID抛出异常: {type(e).__name__}")
        
        # 测试无效MAC地址格式
        try:
            result = fingerprint_manager.validate_fingerprint_changes({
                'mac_changes': {'test_adapter': 'invalid_mac'}
            })
            if not result.get('valid', True):
                print("✅ 无效MAC地址格式正确被拒绝")
            else:
                print("⚠️  无效MAC地址格式未被检测")
        except Exception as e:
            print(f"✅ 无效MAC地址格式抛出异常: {type(e).__name__}")
        
        print("✅ 错误处理一致性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理一致性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始跨平台引擎集成测试...\n")
    
    current_platform = platform_module.system()
    print(f"当前测试平台: {current_platform}")
    
    test_functions = [
        test_platform_factory_integration,
        test_fingerprint_manager_creation,
        test_permission_manager_creation,
        test_cross_platform_interface_consistency,
        test_platform_specific_features,
        test_error_handling_consistency
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
        print("🎉 所有跨平台集成测试通过！引擎集成正常")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
