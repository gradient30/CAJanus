#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户体验测试
测试界面响应性、易用性和用户交互流程
"""

import unittest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer

from core.logger import get_logger


class UserExperienceTestCase(unittest.TestCase):
    """用户体验测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """每个测试方法的初始化"""
        self.logger = get_logger("ux_test")


class ResponsivenessTest(UserExperienceTestCase):
    """界面响应性测试"""
    
    def test_ui_startup_time(self):
        """测试界面启动时间"""
        try:
            from ui.main_window import MainWindow
            
            start_time = time.time()
            main_window = MainWindow()
            main_window.show()
            
            # 等待界面完全加载
            QTest.qWait(100)
            
            end_time = time.time()
            startup_time = end_time - start_time
            
            # 界面启动时间应该在1秒内
            self.assertLess(startup_time, 1.0, f"界面启动时间过长: {startup_time:.2f}秒")
            
            main_window.close()
            self.logger.info(f"界面启动时间: {startup_time:.2f}秒")
            
        except ImportError:
            self.skipTest("主窗口模块不可用")
    
    def test_tab_switching_performance(self):
        """测试标签页切换性能"""
        try:
            from ui.main_window import MainWindow
            
            main_window = MainWindow()
            main_window.show()
            QTest.qWait(100)
            
            tab_widget = main_window.tab_widget
            tab_count = tab_widget.count()
            
            if tab_count > 1:
                # 测试标签页切换时间
                switch_times = []
                
                for i in range(min(tab_count, 5)):  # 最多测试5个标签页
                    start_time = time.time()
                    tab_widget.setCurrentIndex(i)
                    QTest.qWait(50)  # 等待切换完成
                    end_time = time.time()
                    
                    switch_time = end_time - start_time
                    switch_times.append(switch_time)
                
                avg_switch_time = sum(switch_times) / len(switch_times)
                
                # 平均切换时间应该在200ms内
                self.assertLess(avg_switch_time, 0.2, 
                               f"标签页切换时间过长: {avg_switch_time:.3f}秒")
                
                self.logger.info(f"标签页切换平均时间: {avg_switch_time:.3f}秒")
            
            main_window.close()
            
        except ImportError:
            self.skipTest("主窗口模块不可用")
    
    def test_data_refresh_performance(self):
        """测试数据刷新性能"""
        try:
            from ui.system_status_widget import SystemStatusWidget
            
            status_widget = SystemStatusWidget()
            
            # 测试数据刷新时间
            start_time = time.time()
            status_widget.refresh_all_status()
            QTest.qWait(100)
            end_time = time.time()
            
            refresh_time = end_time - start_time
            
            # 数据刷新时间应该在2秒内
            self.assertLess(refresh_time, 2.0, f"数据刷新时间过长: {refresh_time:.2f}秒")
            
            self.logger.info(f"数据刷新时间: {refresh_time:.2f}秒")
            
        except ImportError:
            self.skipTest("系统状态模块不可用")


class UsabilityTest(UserExperienceTestCase):
    """易用性测试"""
    
    def test_keyboard_navigation(self):
        """测试键盘导航"""
        try:
            from ui.main_window import MainWindow
            
            main_window = MainWindow()
            main_window.show()
            QTest.qWait(100)
            
            # 测试Tab键导航
            initial_focus = self.app.focusWidget()
            
            # 模拟Tab键按下
            QTest.keyPress(main_window, Qt.Key_Tab)
            QTest.qWait(50)
            
            new_focus = self.app.focusWidget()
            
            # 焦点应该发生变化（除非只有一个可聚焦控件）
            if main_window.findChildren(QWidget):
                # 如果有多个控件，焦点应该能够移动
                pass  # 这里可以添加更具体的焦点检查
            
            main_window.close()
            self.logger.info("键盘导航测试完成")
            
        except ImportError:
            self.skipTest("主窗口模块不可用")
    
    def test_tooltip_availability(self):
        """测试工具提示可用性"""
        try:
            from ui.main_window import MainWindow
            
            main_window = MainWindow()
            main_window.show()
            QTest.qWait(100)
            
            # 检查主要控件是否有工具提示
            widgets_with_tooltips = 0
            all_widgets = main_window.findChildren(QWidget)
            
            for widget in all_widgets:
                if widget.toolTip():
                    widgets_with_tooltips += 1
            
            # 至少应该有一些控件有工具提示
            self.assertGreater(widgets_with_tooltips, 0, "没有控件设置工具提示")
            
            tooltip_ratio = widgets_with_tooltips / len(all_widgets) if all_widgets else 0
            self.logger.info(f"工具提示覆盖率: {tooltip_ratio:.2%}")
            
            main_window.close()
            
        except ImportError:
            self.skipTest("主窗口模块不可用")
    
    def test_error_message_clarity(self):
        """测试错误信息清晰度"""
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # 测试获取不存在的配置项
        result = config_manager.get_config('non.existent.key', 'default')
        self.assertEqual(result, 'default')
        
        # 测试错误处理是否优雅
        try:
            config_manager.set_config('', 'value')  # 空键名
        except Exception as e:
            # 错误信息应该是有意义的
            error_message = str(e)
            self.assertIsInstance(error_message, str)
            self.assertGreater(len(error_message), 0)
            self.logger.info(f"错误信息示例: {error_message}")


class AccessibilityTest(UserExperienceTestCase):
    """无障碍功能测试"""
    
    def test_high_contrast_mode(self):
        """测试高对比度模式"""
        try:
            from ui.accessibility_manager import get_accessibility_manager, AccessibilityLevel
            
            accessibility_manager = get_accessibility_manager()
            
            # 测试高对比度模式切换
            original_level = accessibility_manager.get_current_level()
            
            accessibility_manager.set_accessibility_level(AccessibilityLevel.HIGH_CONTRAST)
            self.assertEqual(accessibility_manager.get_current_level(), AccessibilityLevel.HIGH_CONTRAST)
            
            # 恢复原设置
            accessibility_manager.set_accessibility_level(original_level)
            
            self.logger.info("高对比度模式测试完成")
            
        except ImportError:
            self.skipTest("无障碍管理器不可用")
    
    def test_keyboard_only_navigation(self):
        """测试纯键盘导航"""
        try:
            from ui.accessibility_manager import get_accessibility_manager, AccessibilityLevel
            
            accessibility_manager = get_accessibility_manager()
            
            # 启用键盘导航模式
            original_level = accessibility_manager.get_current_level()
            accessibility_manager.set_accessibility_level(AccessibilityLevel.KEYBOARD_ONLY)
            
            # 测试快捷键是否工作
            shortcuts = accessibility_manager.keyboard_shortcuts
            self.assertGreater(len(shortcuts), 0, "没有定义键盘快捷键")
            
            # 恢复原设置
            accessibility_manager.set_accessibility_level(original_level)
            
            self.logger.info("键盘导航测试完成")
            
        except ImportError:
            self.skipTest("无障碍管理器不可用")


class ResponsiveDesignTest(UserExperienceTestCase):
    """响应式设计测试"""
    
    def test_different_screen_sizes(self):
        """测试不同屏幕尺寸适配"""
        try:
            from ui.responsive_layout import get_responsive_manager, ScreenSize
            from ui.main_window import MainWindow
            
            responsive_manager = get_responsive_manager()
            main_window = MainWindow()
            
            # 测试不同屏幕尺寸的窗口大小
            for screen_size in ScreenSize:
                responsive_manager.current_screen_size = screen_size
                width, height = responsive_manager.get_optimal_window_size()
                
                self.assertGreater(width, 0, f"{screen_size.value} 屏幕宽度无效")
                self.assertGreater(height, 0, f"{screen_size.value} 屏幕高度无效")
                
                self.logger.info(f"{screen_size.value} 屏幕最佳尺寸: {width}x{height}")
            
            main_window.close()
            
        except ImportError:
            self.skipTest("响应式布局管理器不可用")
    
    def test_dpi_scaling(self):
        """测试DPI缩放"""
        try:
            from ui.responsive_layout import get_responsive_manager, DPIScale
            
            responsive_manager = get_responsive_manager()
            
            # 测试不同DPI缩放下的尺寸计算
            base_size = 100
            
            for dpi_scale in DPIScale:
                responsive_manager.current_dpi_scale = dpi_scale
                scaled_size = responsive_manager.get_scaled_size(base_size)
                
                expected_size = int(base_size * dpi_scale.value)
                self.assertEqual(scaled_size, expected_size, 
                               f"DPI缩放计算错误: {dpi_scale.value}")
                
                self.logger.info(f"DPI {dpi_scale.value} 缩放: {base_size} -> {scaled_size}")
            
        except ImportError:
            self.skipTest("响应式布局管理器不可用")


class InternationalizationTest(UserExperienceTestCase):
    """国际化测试"""
    
    def test_language_switching(self):
        """测试语言切换"""
        try:
            from core.i18n_manager import get_i18n_manager, SupportedLanguage
            
            i18n_manager = get_i18n_manager()
            original_language = i18n_manager.get_current_language()
            
            # 测试切换到不同语言
            for language in SupportedLanguage:
                i18n_manager.set_language(language)
                
                # 测试基本翻译
                app_name = i18n_manager.get_text('app.name')
                self.assertIsNotNone(app_name)
                self.assertNotEqual(app_name, 'app.name')
                
                self.logger.info(f"{language.value} 应用名称: {app_name}")
            
            # 恢复原语言
            i18n_manager.set_language(original_language)
            
        except ImportError:
            self.skipTest("国际化管理器不可用")
    
    def test_date_time_formatting(self):
        """测试日期时间格式化"""
        try:
            from core.i18n_manager import get_i18n_manager, SupportedLanguage
            from datetime import datetime
            
            i18n_manager = get_i18n_manager()
            test_datetime = datetime(2024, 1, 15, 14, 30, 25)
            
            # 测试不同语言的日期时间格式
            for language in [SupportedLanguage.ZH_CN, SupportedLanguage.EN_US]:
                i18n_manager.set_language(language)
                
                formatted_date = i18n_manager.format_datetime(test_datetime, "date")
                formatted_time = i18n_manager.format_datetime(test_datetime, "time")
                formatted_datetime = i18n_manager.format_datetime(test_datetime, "datetime")
                
                self.assertIsNotNone(formatted_date)
                self.assertIsNotNone(formatted_time)
                self.assertIsNotNone(formatted_datetime)
                
                self.logger.info(f"{language.value} 日期格式: {formatted_date}")
                self.logger.info(f"{language.value} 时间格式: {formatted_time}")
                self.logger.info(f"{language.value} 日期时间格式: {formatted_datetime}")
            
        except ImportError:
            self.skipTest("国际化管理器不可用")


class WorkflowTest(UserExperienceTestCase):
    """工作流程测试"""
    
    def test_typical_user_workflow(self):
        """测试典型用户工作流程"""
        try:
            from ui.main_window import MainWindow
            
            main_window = MainWindow()
            main_window.show()
            QTest.qWait(100)
            
            # 模拟用户工作流程
            # 1. 查看系统状态
            if hasattr(main_window, 'system_status_widget'):
                main_window.tab_widget.setCurrentWidget(main_window.system_status_widget)
                QTest.qWait(100)
            
            # 2. 查看设备指纹
            if hasattr(main_window, 'fingerprint_widget'):
                main_window.tab_widget.setCurrentWidget(main_window.fingerprint_widget)
                QTest.qWait(100)
            
            # 3. 访问备份功能
            if hasattr(main_window, 'backup_widget'):
                main_window.tab_widget.setCurrentWidget(main_window.backup_widget)
                QTest.qWait(100)
            
            # 4. 查看教育功能
            if hasattr(main_window, 'education_widget'):
                main_window.tab_widget.setCurrentWidget(main_window.education_widget)
                QTest.qWait(100)
            
            main_window.close()
            self.logger.info("典型用户工作流程测试完成")
            
        except ImportError:
            self.skipTest("主窗口模块不可用")


def run_user_experience_tests():
    """运行所有用户体验测试"""
    test_suite = unittest.TestSuite()
    
    test_classes = [
        ResponsivenessTest,
        UsabilityTest,
        AccessibilityTest,
        ResponsiveDesignTest,
        InternationalizationTest,
        WorkflowTest
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_user_experience_tests()
    sys.exit(0 if success else 1)
