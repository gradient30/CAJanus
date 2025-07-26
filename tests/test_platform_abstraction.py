#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台抽象层测试脚本
验证配置管理、日志系统和平台工厂的基本功能
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_config_manager():
    """测试配置管理器"""
    print("=== 测试配置管理器 ===")
    
    try:
        from core.config_manager import ConfigManager
        
        # 创建配置管理器实例
        config = ConfigManager()
        
        # 测试基本配置获取
        app_name = config.get_config('app.name', '默认应用名')
        print(f"应用名称: {app_name}")
        
        # 测试配置设置
        config.set_config('test.value', 'test_data')
        test_value = config.get_config('test.value')
        print(f"测试配置值: {test_value}")
        
        # 测试便捷方法
        print(f"调试模式: {config.is_debug_mode()}")
        print(f"学习模式: {config.is_learning_mode()}")
        print(f"界面语言: {config.get_ui_language()}")
        print(f"窗口大小: {config.get_window_size()}")
        
        # 测试目录创建
        backup_dir = config.get_backup_directory()
        log_dir = config.get_log_directory()
        print(f"备份目录: {backup_dir}")
        print(f"日志目录: {log_dir}")
        
        # 测试配置验证
        is_valid = config.validate_config()
        print(f"配置验证结果: {is_valid}")
        
        print("✅ 配置管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def test_logger():
    """测试日志系统"""
    print("\n=== 测试日志系统 ===")
    
    try:
        from core.logger import get_logger, get_audit_logger
        from core.interfaces import OperationRecord, OperationType, RiskLevel
        from datetime import datetime
        
        # 测试基本日志记录
        logger = get_logger("test")
        logger.info("这是一条测试信息")
        logger.warning("这是一条测试警告")
        logger.error("这是一条测试错误")
        
        # 测试审计日志
        audit_logger = get_audit_logger()
        
        # 创建测试操作记录
        test_record = OperationRecord(
            operation_id="test_001",
            timestamp=datetime.now(),
            operation_type=OperationType.READ,
            target="test_target",
            parameters={"param1": "value1"},
            result="success",
            backup_id=None,
            risk_level=RiskLevel.LOW,
            user="test_user",
            duration=0.5
        )
        
        # 记录操作日志
        audit_logger.log_operation(test_record)
        
        # 记录安全事件
        audit_logger.log_security_event("test_event", {
            "description": "测试安全事件",
            "severity": "low"
        })
        
        # 测试日志查询
        history = audit_logger.get_operation_history(limit=5)
        print(f"操作历史记录数量: {len(history)}")
        
        print("✅ 日志系统测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        return False

def test_platform_factory():
    """测试平台工厂"""
    print("\n=== 测试平台工厂 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        
        # 测试平台信息
        platform_info = factory.get_platform_info()
        print(f"平台信息: {platform_info['system']} {platform_info['release']}")
        
        # 测试平台支持检查
        is_supported = factory.is_supported_platform()
        print(f"平台支持状态: {is_supported}")
        
        # 测试平台功能
        capabilities = factory.get_platform_capabilities()
        print(f"平台功能: {list(capabilities.keys())}")
        
        # 测试支持的平台列表
        supported_platforms = factory.get_supported_platforms()
        print(f"支持的平台: {supported_platforms}")
        
        print("✅ 平台工厂测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 平台工厂测试失败: {e}")
        return False

def test_windows_permission_manager():
    """测试Windows权限管理器（仅在Windows平台）"""
    print("\n=== 测试Windows权限管理器 ===")
    
    try:
        import platform as platform_module
        if platform_module.system() != 'Windows':
            print("⏭️  跳过Windows权限管理器测试（非Windows平台）")
            return True
        
        from platforms.windows.permission_manager import WindowsPermissionManager
        
        perm_manager = WindowsPermissionManager()
        
        # 测试权限检查
        is_admin = perm_manager.check_admin_privileges()
        print(f"管理员权限: {is_admin}")
        
        # 测试用户信息
        current_user = perm_manager.get_current_user()
        print(f"当前用户: {current_user}")
        
        # 测试UAC状态
        uac_enabled = perm_manager.check_uac_enabled()
        print(f"UAC启用状态: {uac_enabled}")
        
        # 测试权限信息
        perm_info = perm_manager.get_permission_info()
        print(f"权限信息: {perm_info}")
        
        # 测试注册表访问权限
        registry_access = perm_manager.check_registry_access(
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        )
        print(f"注册表访问权限: {registry_access}")
        
        print("✅ Windows权限管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Windows权限管理器测试失败: {e}")
        return False

def test_interfaces():
    """测试接口定义"""
    print("\n=== 测试接口定义 ===")
    
    try:
        from core.interfaces import (
            NetworkAdapter, BackupInfo, OperationRecord, ValidationResult,
            RiskLevel, OperationType, AdapterType
        )
        from datetime import datetime
        
        # 测试数据结构创建
        adapter = NetworkAdapter(
            id="test_adapter",
            name="Test Adapter",
            description="Test Network Adapter",
            mac_address="00:11:22:33:44:55",
            status="active",
            adapter_type=AdapterType.ETHERNET,
            can_modify=True
        )
        print(f"网络适配器: {adapter.name} - {adapter.mac_address}")
        
        # 测试验证结果
        validation = ValidationResult()
        validation.add_warning("这是一个测试警告")
        validation.add_error("这是一个测试错误")
        print(f"验证结果: 有效={validation.is_valid}, 错误数={len(validation.errors)}")
        
        print("✅ 接口定义测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 接口定义测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始平台抽象层测试...\n")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(test_config_manager())
    test_results.append(test_logger())
    test_results.append(test_platform_factory())
    test_results.append(test_windows_permission_manager())
    test_results.append(test_interfaces())
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！平台抽象层基础功能正常")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
