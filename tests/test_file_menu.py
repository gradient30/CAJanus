#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件菜单功能测试脚本
"""

import sys
import os
import json
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager

def test_config_operations():
    """测试配置操作"""
    print("=== 配置管理功能测试 ===")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 测试1: 获取当前配置
    print("\n1. 当前配置:")
    current_config = config_manager.config
    print(f"应用名称: {config_manager.get_config('app.name', 'N/A')}")
    print(f"应用版本: {config_manager.get_config('app.version', 'N/A')}")
    print(f"日志级别: {config_manager.get_config('logging.level', 'N/A')}")
    
    # 测试2: 保存配置到文件
    print("\n2. 测试保存配置:")
    test_save_path = "test_config_save.json"
    try:
        success = config_manager.save_to_file(test_save_path)
        if success and os.path.exists(test_save_path):
            print(f"✅ 配置保存成功: {test_save_path}")
            
            # 检查文件内容
            with open(test_save_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f) if test_save_path.endswith('.json') else f.read()
                print(f"文件大小: {os.path.getsize(test_save_path)} 字节")
        else:
            print("❌ 配置保存失败")
    except Exception as e:
        print(f"❌ 保存配置时出错: {e}")
    
    # 测试3: 修改配置并保存
    print("\n3. 测试配置修改:")
    original_name = config_manager.get_config('app.name', '')
    config_manager.set_config('app.name', '测试应用名称')
    config_manager.set_config('test.new_setting', 'test_value')
    
    test_modified_path = "test_config_modified.json"
    success = config_manager.save_to_file(test_modified_path)
    if success:
        print(f"✅ 修改后的配置保存成功: {test_modified_path}")
    else:
        print("❌ 修改后的配置保存失败")
    
    # 测试4: 从文件加载配置
    print("\n4. 测试加载配置:")
    if os.path.exists(test_modified_path):
        # 先重置配置
        config_manager.reset_to_defaults()
        print(f"重置后应用名称: {config_manager.get_config('app.name', 'N/A')}")
        
        # 加载修改后的配置
        success = config_manager.load_from_file(test_modified_path)
        if success:
            loaded_name = config_manager.get_config('app.name', 'N/A')
            loaded_test = config_manager.get_config('test.new_setting', 'N/A')
            print(f"✅ 配置加载成功")
            print(f"加载后应用名称: {loaded_name}")
            print(f"加载后测试设置: {loaded_test}")
        else:
            print("❌ 配置加载失败")
    
    # 测试5: 重置到默认配置
    print("\n5. 测试重置配置:")
    try:
        config_manager.reset_to_defaults()
        reset_name = config_manager.get_config('app.name', 'N/A')
        print(f"✅ 配置重置成功")
        print(f"重置后应用名称: {reset_name}")
    except Exception as e:
        print(f"❌ 配置重置失败: {e}")
    
    # 测试6: 错误处理
    print("\n6. 测试错误处理:")
    
    # 测试加载不存在的文件
    success = config_manager.load_from_file("nonexistent_file.json")
    if not success:
        print("✅ 正确处理了不存在的文件")
    else:
        print("❌ 未正确处理不存在的文件")
    
    # 测试保存到无效路径
    success = config_manager.save_to_file("/invalid/path/config.json")
    if not success:
        print("✅ 正确处理了无效的保存路径")
    else:
        print("❌ 未正确处理无效的保存路径")
    
    # 清理测试文件
    print("\n7. 清理测试文件:")
    for test_file in [test_save_path, test_modified_path]:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"已删除测试文件: {test_file}")
    
    print("\n=== 配置管理功能测试完成 ===")

if __name__ == "__main__":
    test_config_operations()
