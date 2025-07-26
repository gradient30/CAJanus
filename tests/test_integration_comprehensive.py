#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面集成测试
测试所有功能模块的集成和协作
"""

import unittest
import sys
import os
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer

from core.config_manager import ConfigManager
from core.platform_factory import get_platform_factory
from core.logger import get_logger
from core.i18n_manager import get_i18n_manager, SupportedLanguage
from ui.responsive_layout import get_responsive_manager
from ui.accessibility_manager import get_accessibility_manager, AccessibilityLevel


class IntegrationTestCase(unittest.TestCase):
    """集成测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建QApplication实例
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        
        # 创建临时目录
        cls.temp_dir = tempfile.mkdtemp()
        
        # 设置测试环境
        os.environ['JANUS_TEST_MODE'] = '1'
        os.environ['JANUS_CONFIG_DIR'] = cls.temp_dir
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 清理临时目录
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
        
        # 清理环境变量
        if 'JANUS_TEST_MODE' in os.environ:
            del os.environ['JANUS_TEST_MODE']
        if 'JANUS_CONFIG_DIR' in os.environ:
            del os.environ['JANUS_CONFIG_DIR']
    
    def setUp(self):
        """每个测试方法的初始化"""
        self.logger = get_logger("integration_test")
        self.config_manager = ConfigManager()
        self.platform_factory = get_platform_factory()
        self.i18n_manager = get_i18n_manager()
        self.responsive_manager = get_responsive_manager()
        self.accessibility_manager = get_accessibility_manager()


class CoreModulesIntegrationTest(IntegrationTestCase):
    """核心模块集成测试"""
    
    def test_config_manager_integration(self):
        """测试配置管理器集成"""
        # 测试配置加载
        self.assertIsNotNone(self.config_manager.get_config('app.name'))
        
        # 测试配置设置和保存
        test_value = "test_integration_value"
        self.config_manager.set_config('test.integration', test_value)
        self.assertEqual(self.config_manager.get_config('test.integration'), test_value)
        
        # 测试配置验证
        self.assertTrue(self.config_manager.validate_config())
    
    def test_platform_factory_integration(self):
        """测试平台工厂集成"""
        # 测试平台检测
        platform = self.platform_factory.get_current_platform()
        self.assertIsNotNone(platform)
        
        # 测试平台引擎获取
        engine = self.platform_factory.get_fingerprint_engine()
        self.assertIsNotNone(engine)
        
        # 测试权限管理器
        permission_manager = self.platform_factory.get_permission_manager()
        self.assertIsNotNone(permission_manager)
    
    def test_i18n_manager_integration(self):
        """测试国际化管理器集成"""
        # 测试语言切换
        original_language = self.i18n_manager.get_current_language()
        
        # 切换到英文
        self.i18n_manager.set_language(SupportedLanguage.EN_US)
        self.assertEqual(self.i18n_manager.get_current_language(), SupportedLanguage.EN_US)
        
        # 测试翻译获取
        app_name = self.i18n_manager.get_text('app.name')
        self.assertIsNotNone(app_name)
        self.assertNotEqual(app_name, 'app.name')  # 应该有实际翻译
        
        # 恢复原语言
        self.i18n_manager.set_language(original_language)
    
    def test_responsive_manager_integration(self):
        """测试响应式管理器集成"""
        # 测试屏幕尺寸检测
        screen_size = self.responsive_manager.detect_screen_size()
        self.assertIsNotNone(screen_size)
        
        # 测试DPI检测
        dpi_scale = self.responsive_manager.detect_dpi_scale()
        self.assertIsNotNone(dpi_scale)
        
        # 测试最佳窗口尺寸获取
        width, height = self.responsive_manager.get_optimal_window_size()
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
    
    def test_accessibility_manager_integration(self):
        """测试无障碍管理器集成"""
        # 测试无障碍级别设置
        original_level = self.accessibility_manager.get_current_level()
        
        # 设置高对比度模式
        self.accessibility_manager.set_accessibility_level(AccessibilityLevel.HIGH_CONTRAST)
        self.assertEqual(self.accessibility_manager.get_current_level(), AccessibilityLevel.HIGH_CONTRAST)
        
        # 恢复原设置
        self.accessibility_manager.set_accessibility_level(original_level)


class UIModulesIntegrationTest(IntegrationTestCase):
    """UI模块集成测试"""
    
    def test_main_window_integration(self):
        """测试主窗口集成"""
        try:
            from ui.main_window import MainWindow
            
            # 创建主窗口
            main_window = MainWindow()
            self.assertIsNotNone(main_window)
            
            # 测试窗口初始化
            self.assertIsNotNone(main_window.config_manager)
            self.assertIsNotNone(main_window.platform_factory)
            
            # 测试标签页创建
            self.assertIsNotNone(main_window.tab_widget)
            self.assertGreater(main_window.tab_widget.count(), 0)
            
            # 清理
            main_window.close()
            
        except ImportError as e:
            self.skipTest(f"主窗口模块不可用: {e}")
    
    def test_settings_dialog_integration(self):
        """测试设置对话框集成"""
        try:
            from ui.settings_dialog import SettingsDialog
            
            # 创建设置对话框
            settings_dialog = SettingsDialog(self.config_manager)
            self.assertIsNotNone(settings_dialog)
            
            # 测试设置加载
            settings_dialog.load_all_settings()
            
            # 测试设置保存
            settings_dialog.save_all_settings()
            
            # 清理
            settings_dialog.close()
            
        except ImportError as e:
            self.skipTest(f"设置对话框模块不可用: {e}")
    
    def test_help_system_integration(self):
        """测试帮助系统集成"""
        try:
            from ui.help_system import HelpSystemDialog
            
            # 创建帮助系统
            help_dialog = HelpSystemDialog()
            self.assertIsNotNone(help_dialog)
            
            # 测试帮助内容加载
            self.assertIsNotNone(help_dialog.quick_help_widget)
            self.assertIsNotNone(help_dialog.content_widget)
            
            # 清理
            help_dialog.close()
            
        except ImportError as e:
            self.skipTest(f"帮助系统模块不可用: {e}")


class FunctionalIntegrationTest(IntegrationTestCase):
    """功能集成测试"""
    
    def test_backup_restore_integration(self):
        """测试备份恢复集成"""
        try:
            from ui.backup_widget import BackupWidget
            
            # 创建备份控件
            backup_widget = BackupWidget()
            self.assertIsNotNone(backup_widget)
            
            # 测试备份目录创建
            backup_dir = self.config_manager.get_backup_directory()
            self.assertTrue(backup_dir.exists())
            
            # 清理
            backup_widget.close()
            
        except ImportError as e:
            self.skipTest(f"备份模块不可用: {e}")
    
    def test_fingerprint_detection_integration(self):
        """测试指纹检测集成"""
        try:
            from ui.fingerprint_widget import FingerprintWidget
            
            # 创建指纹控件
            fingerprint_widget = FingerprintWidget()
            self.assertIsNotNone(fingerprint_widget)
            
            # 测试数据刷新
            fingerprint_widget.refresh_all_data()
            
            # 清理
            fingerprint_widget.close()
            
        except ImportError as e:
            self.skipTest(f"指纹检测模块不可用: {e}")
    
    def test_system_status_integration(self):
        """测试系统状态集成"""
        try:
            from ui.system_status_widget import SystemStatusWidget
            
            # 创建系统状态控件
            status_widget = SystemStatusWidget()
            self.assertIsNotNone(status_widget)
            
            # 测试状态刷新
            status_widget.refresh_all_status()
            
            # 清理
            status_widget.close()
            
        except ImportError as e:
            self.skipTest(f"系统状态模块不可用: {e}")


class PerformanceIntegrationTest(IntegrationTestCase):
    """性能集成测试"""
    
    def test_startup_performance(self):
        """测试启动性能"""
        start_time = time.time()
        
        # 模拟应用启动过程
        config_manager = ConfigManager()
        platform_factory = get_platform_factory()
        i18n_manager = get_i18n_manager()
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        # 启动时间应该在合理范围内（< 5秒）
        self.assertLess(startup_time, 5.0, f"启动时间过长: {startup_time:.2f}秒")
        self.logger.info(f"启动性能测试通过，耗时: {startup_time:.2f}秒")
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import gc
        
        # 获取初始内存使用
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # 执行一些操作
        for _ in range(100):
            config_manager = ConfigManager()
            _ = config_manager.get_config('app.name')
        
        # 强制垃圾回收
        gc.collect()
        
        # 获取最终内存使用
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（< 50MB）
        max_increase = 50 * 1024 * 1024  # 50MB
        self.assertLess(memory_increase, max_increase, 
                       f"内存增长过多: {memory_increase / 1024 / 1024:.2f}MB")
        
        self.logger.info(f"内存使用测试通过，增长: {memory_increase / 1024 / 1024:.2f}MB")
    
    def test_response_time(self):
        """测试响应时间"""
        # 测试配置获取响应时间
        start_time = time.time()
        for _ in range(1000):
            _ = self.config_manager.get_config('app.name')
        end_time = time.time()
        
        avg_response_time = (end_time - start_time) / 1000
        
        # 平均响应时间应该很快（< 1ms）
        self.assertLess(avg_response_time, 0.001, 
                       f"配置获取响应时间过慢: {avg_response_time * 1000:.2f}ms")
        
        self.logger.info(f"响应时间测试通过，平均: {avg_response_time * 1000:.4f}ms")


class ErrorHandlingIntegrationTest(IntegrationTestCase):
    """错误处理集成测试"""
    
    def test_config_error_handling(self):
        """测试配置错误处理"""
        # 测试无效配置键
        result = self.config_manager.get_config('invalid.key', 'default_value')
        self.assertEqual(result, 'default_value')
        
        # 测试配置验证错误处理
        with patch.object(self.config_manager, 'get_backup_directory', 
                         side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                self.config_manager.validate_config()
    
    def test_platform_error_handling(self):
        """测试平台错误处理"""
        # 测试平台检测错误处理
        with patch('platform.system', side_effect=Exception("Test error")):
            # 应该有默认的错误处理机制
            platform = self.platform_factory.get_current_platform()
            self.assertIsNotNone(platform)
    
    def test_i18n_error_handling(self):
        """测试国际化错误处理"""
        # 测试无效翻译键
        result = self.i18n_manager.get_text('invalid.key')
        self.assertEqual(result, 'invalid.key')  # 应该返回键名
        
        # 测试无效语言设置
        from core.i18n_manager import SupportedLanguage
        original_language = self.i18n_manager.get_current_language()
        
        # 尝试设置无效语言（应该不会崩溃）
        with patch.object(self.i18n_manager, 'translations', {}):
            self.i18n_manager.set_language(SupportedLanguage.EN_US)
            # 应该仍然能正常工作


def run_integration_tests():
    """运行所有集成测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        CoreModulesIntegrationTest,
        UIModulesIntegrationTest,
        FunctionalIntegrationTest,
        PerformanceIntegrationTest,
        ErrorHandlingIntegrationTest
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
