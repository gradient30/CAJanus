#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框功能测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.settings_dialog import SettingsDialog
from core.config_manager import ConfigManager

def test_settings_dialog():
    """测试设置对话框"""
    print("=== 设置对话框功能测试 ===")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 测试1: 检查默认配置值
    print("\n1. 检查默认配置值:")
    test_configs = [
        ('ui.show_splash_screen', True),
        ('ui.minimize_to_tray', False),
        ('app.check_updates_on_startup', True),
        ('app.auto_save_config', True),
        ('ui.theme', '默认'),
        ('ui.font_size', 10),
        ('ui.transparency', 100),
        ('ui.show_tooltips', True),
        ('ui.language', '简体中文'),
        ('ui.date_format', 'YYYY-MM-DD'),
        ('security.three_level_confirmation', True),
        ('security.mac_modification_confirmation', True),
        ('security.guid_modification_confirmation', True),
        ('security.restore_confirmation', True),
        ('backup.auto_backup_before_operation', True),
        ('backup.retention_days', 30),
        ('backup.compression_enabled', True),
        ('backup.encryption_enabled', False),
        ('logging.level', 'INFO'),
        ('logging.audit_enabled', True),
        ('logging.max_file_size_mb', 10),
        ('performance.enable_cache', True),
        ('performance.cache_expire_seconds', 300),
        ('performance.enable_parallel_query', False),
        ('performance.max_threads', 4),
        ('developer.debug_mode', False),
        ('developer.show_internal_errors', False),
        ('developer.performance_monitoring', False),
        ('experimental.enable_features', False)
    ]
    
    for config_key, expected_default in test_configs:
        actual_value = config_manager.get_config(config_key, None)
        if actual_value is None:
            # 如果配置不存在，使用期望的默认值
            config_manager.set_config(config_key, expected_default)
            actual_value = expected_default
            status = "🔧 已设置默认值"
        elif actual_value == expected_default:
            status = "✅ 正确"
        else:
            status = f"⚠️  期望: {expected_default}, 实际: {actual_value}"
        
        print(f"  {config_key}: {actual_value} {status}")
    
    # 测试2: 配置修改和保存
    print("\n2. 测试配置修改:")
    test_modifications = [
        ('ui.theme', '深色'),
        ('ui.font_size', 12),
        ('security.three_level_confirmation', False),
        ('backup.retention_days', 60),
        ('logging.level', 'DEBUG'),
        ('performance.max_threads', 8),
        ('developer.debug_mode', True)
    ]
    
    for config_key, new_value in test_modifications:
        old_value = config_manager.get_config(config_key)
        config_manager.set_config(config_key, new_value)
        actual_value = config_manager.get_config(config_key)
        
        if actual_value == new_value:
            print(f"  ✅ {config_key}: {old_value} → {new_value}")
        else:
            print(f"  ❌ {config_key}: 修改失败，仍为 {actual_value}")
    
    # 测试3: 配置保存和加载
    print("\n3. 测试配置保存和加载:")
    try:
        config_manager.save_config()
        print("  ✅ 配置保存成功")
        
        # 创建新的配置管理器实例来测试加载
        new_config_manager = ConfigManager()
        
        # 验证修改的配置是否正确加载
        for config_key, expected_value in test_modifications:
            loaded_value = new_config_manager.get_config(config_key)
            if loaded_value == expected_value:
                print(f"  ✅ {config_key}: 加载正确 ({loaded_value})")
            else:
                print(f"  ❌ {config_key}: 加载错误，期望 {expected_value}，实际 {loaded_value}")
                
    except Exception as e:
        print(f"  ❌ 配置保存/加载失败: {e}")
    
    # 测试4: 重置配置
    print("\n4. 测试配置重置:")
    try:
        config_manager.reset_to_defaults()
        print("  ✅ 配置重置成功")
        
        # 验证重置后的值
        for config_key, expected_default in test_configs[:5]:  # 只检查前5个
            actual_value = config_manager.get_config(config_key, None)
            if actual_value == expected_default:
                print(f"  ✅ {config_key}: 重置正确 ({actual_value})")
            else:
                print(f"  ⚠️  {config_key}: 重置后为 {actual_value}，期望 {expected_default}")
                
    except Exception as e:
        print(f"  ❌ 配置重置失败: {e}")
    
    print("\n=== 设置对话框功能测试完成 ===")

def test_settings_dialog_ui():
    """测试设置对话框UI"""
    print("\n=== 设置对话框UI测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建设置对话框
        dialog = SettingsDialog()
        
        print("✅ 设置对话框创建成功")
        print(f"  窗口标题: {dialog.windowTitle()}")
        print(f"  窗口大小: {dialog.size().width()}x{dialog.size().height()}")
        print(f"  标签页数量: {dialog.tab_widget.count()}")
        
        # 检查标签页
        for i in range(dialog.tab_widget.count()):
            tab_text = dialog.tab_widget.tabText(i)
            print(f"  标签页 {i+1}: {tab_text}")
        
        # 显示对话框（非模态，用于测试）
        dialog.setModal(False)
        dialog.show()
        
        print("✅ 设置对话框UI测试完成")
        print("请手动测试各个设置项的功能")
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 设置对话框UI测试失败: {e}")
        return 1

if __name__ == "__main__":
    # 运行配置测试
    test_settings_dialog()
    
    # 询问是否运行UI测试
    response = input("\n是否运行UI测试？(y/n): ").lower().strip()
    if response == 'y':
        sys.exit(test_settings_dialog_ui())
