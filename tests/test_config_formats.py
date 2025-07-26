#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件格式兼容性测试脚本
"""

import sys
import os
import json
import yaml
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager

def test_config_formats():
    """测试配置文件格式兼容性"""
    print("=== 配置文件格式兼容性测试 ===")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 设置一些测试配置
    test_configs = {
        'ui.theme': 'dark',
        'ui.language': 'zh_CN',
        'ui.font_size': 12,
        'security.three_level_confirmation': False,
        'backup.retention_days': 60,
        'logging.level': 'DEBUG'
    }
    
    print("\n1. 设置测试配置:")
    for key, value in test_configs.items():
        config_manager.set_config(key, value)
        print(f"  {key}: {value}")
    
    # 测试YAML格式保存和加载
    print("\n2. 测试YAML格式:")
    yaml_file = "test_config.yaml"
    try:
        # 保存为YAML
        success = config_manager.save_to_file(yaml_file)
        if success and os.path.exists(yaml_file):
            print(f"  ✅ YAML保存成功: {yaml_file}")
            
            # 检查文件内容
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml_content = f.read()
                print(f"  文件大小: {len(yaml_content)} 字符")
                
            # 创建新的配置管理器并加载
            new_config_manager = ConfigManager()
            success = new_config_manager.load_from_file(yaml_file)
            if success:
                print("  ✅ YAML加载成功")
                
                # 验证配置
                for key, expected_value in test_configs.items():
                    actual_value = new_config_manager.get_config(key)
                    if actual_value == expected_value:
                        print(f"    ✅ {key}: {actual_value}")
                    else:
                        print(f"    ❌ {key}: 期望 {expected_value}, 实际 {actual_value}")
            else:
                print("  ❌ YAML加载失败")
        else:
            print("  ❌ YAML保存失败")
    except Exception as e:
        print(f"  ❌ YAML测试失败: {e}")
    
    # 测试JSON格式保存和加载
    print("\n3. 测试JSON格式:")
    json_file = "test_config.json"
    try:
        # 保存为JSON
        success = config_manager.save_to_file(json_file)
        if success and os.path.exists(json_file):
            print(f"  ✅ JSON保存成功: {json_file}")
            
            # 检查文件内容
            with open(json_file, 'r', encoding='utf-8') as f:
                json_content = f.read()
                print(f"  文件大小: {len(json_content)} 字符")
                
            # 创建新的配置管理器并加载
            new_config_manager = ConfigManager()
            success = new_config_manager.load_from_file(json_file)
            if success:
                print("  ✅ JSON加载成功")
                
                # 验证配置
                for key, expected_value in test_configs.items():
                    actual_value = new_config_manager.get_config(key)
                    if actual_value == expected_value:
                        print(f"    ✅ {key}: {actual_value}")
                    else:
                        print(f"    ❌ {key}: 期望 {expected_value}, 实际 {actual_value}")
            else:
                print("  ❌ JSON加载失败")
        else:
            print("  ❌ JSON保存失败")
    except Exception as e:
        print(f"  ❌ JSON测试失败: {e}")
    
    # 测试格式互转
    print("\n4. 测试格式互转:")
    try:
        # YAML -> JSON
        yaml_to_json_manager = ConfigManager()
        yaml_to_json_manager.load_from_file(yaml_file)
        yaml_to_json_manager.save_to_file("yaml_to_json.json")
        
        # JSON -> YAML
        json_to_yaml_manager = ConfigManager()
        json_to_yaml_manager.load_from_file(json_file)
        json_to_yaml_manager.save_to_file("json_to_yaml.yaml")
        
        print("  ✅ 格式互转成功")
        
        # 验证转换后的内容
        with open("yaml_to_json.json", 'r', encoding='utf-8') as f:
            converted_json = json.load(f)
        
        with open("json_to_yaml.yaml", 'r', encoding='utf-8') as f:
            converted_yaml = yaml.safe_load(f)
        
        # 检查关键配置是否一致
        for key in ['ui.theme', 'ui.font_size', 'logging.level']:
            json_val = converted_json.get('ui', {}).get(key.split('.')[1]) if key.startswith('ui.') else converted_json.get(key.split('.')[0], {}).get(key.split('.')[1])
            yaml_val = converted_yaml.get('ui', {}).get(key.split('.')[1]) if key.startswith('ui.') else converted_yaml.get(key.split('.')[0], {}).get(key.split('.')[1])
            
            if json_val == yaml_val:
                print(f"    ✅ {key}: 转换一致")
            else:
                print(f"    ⚠️  {key}: JSON={json_val}, YAML={yaml_val}")
                
    except Exception as e:
        print(f"  ❌ 格式互转测试失败: {e}")
    
    # 测试新建配置功能
    print("\n5. 测试新建配置功能:")
    try:
        # 重置到默认配置
        config_manager.reset_to_defaults()
        
        # 保存为YAML（默认格式）
        config_manager.save_to_file("new_config.yaml")
        
        # 保存为JSON
        config_manager.save_to_file("new_config.json")
        
        print("  ✅ 新建配置功能正常")
        
        # 检查默认配置是否正确加载
        default_theme = config_manager.get_config('ui.theme', 'unknown')
        default_language = config_manager.get_config('ui.language', 'unknown')
        
        print(f"    默认主题: {default_theme}")
        print(f"    默认语言: {default_language}")
        
    except Exception as e:
        print(f"  ❌ 新建配置测试失败: {e}")
    
    # 清理测试文件
    print("\n6. 清理测试文件:")
    test_files = [
        "test_config.yaml", "test_config.json",
        "yaml_to_json.json", "json_to_yaml.yaml",
        "new_config.yaml", "new_config.json"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"  已删除: {test_file}")
    
    print("\n=== 配置文件格式兼容性测试完成 ===")

if __name__ == "__main__":
    test_config_formats()
