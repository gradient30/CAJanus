#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本
单独测试各个组件以排查问题
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_basic_imports():
    """测试基本导入"""
    print("=== 测试基本导入 ===")
    
    try:
        # 测试接口导入
        from core.interfaces import NetworkAdapter, RiskLevel
        print("✅ 接口导入成功")
        
        # 测试异常导入
        from core.exceptions import JanusException
        print("✅ 异常类导入成功")
        
        # 测试配置管理器导入
        from core.config_manager import ConfigManager
        config = ConfigManager()
        print(f"✅ 配置管理器导入成功，应用名: {config.get_config('app.name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本导入失败: {e}")
        return False

def test_logger_simple():
    """简单测试日志系统"""
    print("\n=== 测试日志系统 ===")
    
    try:
        from core.logger import get_logger
        logger = get_logger("test_simple")
        logger.info("测试日志消息")
        print("✅ 日志系统工作正常")
        return True
        
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        return False

def test_platform_detection():
    """测试平台检测"""
    print("\n=== 测试平台检测 ===")
    
    try:
        import platform as platform_module
        system = platform_module.system()
        print(f"当前平台: {system}")
        
        # 测试平台工厂的基本功能
        from core.platform_factory import PlatformFactory
        factory = PlatformFactory()
        print(f"平台工厂检测到的系统: {factory.current_platform}")
        
        platform_info = factory.get_platform_info()
        print(f"平台详细信息: {platform_info['system']} {platform_info['release']}")
        
        print("✅ 平台检测正常")
        return True
        
    except Exception as e:
        print(f"❌ 平台检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_windows_permission_simple():
    """简单测试Windows权限管理"""
    print("\n=== 测试Windows权限管理 ===")
    
    try:
        import platform as platform_module
        if platform_module.system() != 'Windows':
            print("⏭️  跳过Windows权限测试（非Windows平台）")
            return True
        
        from platforms.windows.permission_manager import WindowsPermissionManager
        perm_manager = WindowsPermissionManager()
        
        is_admin = perm_manager.check_admin_privileges()
        user = perm_manager.get_current_user()
        
        print(f"管理员权限: {is_admin}")
        print(f"当前用户: {user}")
        print("✅ Windows权限管理正常")
        return True
        
    except Exception as e:
        print(f"❌ Windows权限管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始简化测试...\n")
    
    tests = [
        test_basic_imports,
        test_logger_simple,
        test_platform_detection,
        test_windows_permission_simple
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
