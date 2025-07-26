#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试平台工厂注册问题
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def debug_platform_factory():
    """调试平台工厂"""
    print("=== 调试平台工厂 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        
        print(f"当前平台: {factory.current_platform}")
        print(f"设备指纹管理器注册表: {list(factory._fingerprint_managers.keys())}")
        print(f"权限管理器注册表: {list(factory._permission_managers.keys())}")
        
        # 尝试手动注册
        print("\n尝试手动注册Windows实现...")
        try:
            from platforms.windows.fingerprint_manager import WindowsFingerprintManager
            from platforms.windows.permission_manager import WindowsPermissionManager
            
            factory.register_fingerprint_manager('Windows', WindowsFingerprintManager)
            factory.register_permission_manager('Windows', WindowsPermissionManager)
            
            print("✅ 手动注册成功")
            print(f"设备指纹管理器注册表: {list(factory._fingerprint_managers.keys())}")
            print(f"权限管理器注册表: {list(factory._permission_managers.keys())}")
            
            # 测试创建
            fingerprint_manager = factory.create_fingerprint_manager()
            permission_manager = factory.create_permission_manager()
            
            print(f"✅ 创建成功:")
            print(f"  设备指纹管理器: {type(fingerprint_manager).__name__}")
            print(f"  权限管理器: {type(permission_manager).__name__}")
            
        except Exception as e:
            print(f"❌ 手动注册失败: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_platform_factory()
