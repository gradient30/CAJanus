#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框
提供应用程序的配置和个性化设置
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QComboBox, QCheckBox, QSpinBox, QTabWidget,
    QWidget, QFileDialog, QDialogButtonBox, QTextEdit,
    QSlider, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.logger import get_logger


class GeneralSettingsWidget(QWidget):
    """常规设置控件"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 应用程序设置组
        app_group = QGroupBox("应用程序设置")
        app_layout = QGridLayout(app_group)
        
        # 启动时显示启动画面
        app_layout.addWidget(QLabel("启动时显示启动画面:"), 0, 0)
        self.show_splash_check = QCheckBox()
        app_layout.addWidget(self.show_splash_check, 0, 1)
        
        # 最小化到系统托盘
        app_layout.addWidget(QLabel("最小化到系统托盘:"), 1, 0)
        self.minimize_to_tray_check = QCheckBox()
        app_layout.addWidget(self.minimize_to_tray_check, 1, 1)
        
        # 启动时检查更新
        app_layout.addWidget(QLabel("启动时检查更新:"), 2, 0)
        self.check_updates_check = QCheckBox()
        app_layout.addWidget(self.check_updates_check, 2, 1)
        
        # 自动保存配置
        app_layout.addWidget(QLabel("自动保存配置:"), 3, 0)
        self.auto_save_check = QCheckBox()
        app_layout.addWidget(self.auto_save_check, 3, 1)
        
        layout.addWidget(app_group)
        
        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QGridLayout(ui_group)
        
        # 主题选择
        ui_layout.addWidget(QLabel("界面主题:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认", "深色", "浅色", "高对比度"])
        ui_layout.addWidget(self.theme_combo, 0, 1)
        
        # 字体大小
        ui_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setSuffix(" pt")
        ui_layout.addWidget(self.font_size_spin, 1, 1)
        
        # 窗口透明度
        ui_layout.addWidget(QLabel("窗口透明度:"), 2, 0)
        transparency_layout = QHBoxLayout()
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(70, 100)
        self.transparency_slider.setValue(100)
        self.transparency_label = QLabel("100%")
        self.transparency_slider.valueChanged.connect(
            lambda v: self.transparency_label.setText(f"{v}%")
        )
        transparency_layout.addWidget(self.transparency_slider)
        transparency_layout.addWidget(self.transparency_label)
        ui_layout.addLayout(transparency_layout, 2, 1)
        
        # 显示工具提示
        ui_layout.addWidget(QLabel("显示工具提示:"), 3, 0)
        self.show_tooltips_check = QCheckBox()
        ui_layout.addWidget(self.show_tooltips_check, 3, 1)
        
        layout.addWidget(ui_group)
        
        # 语言设置组
        lang_group = QGroupBox("语言设置")
        lang_layout = QGridLayout(lang_group)
        
        # 界面语言
        lang_layout.addWidget(QLabel("界面语言:"), 0, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English", "繁體中文", "日本語"])
        lang_layout.addWidget(self.language_combo, 0, 1)
        
        # 日期格式
        lang_layout.addWidget(QLabel("日期格式:"), 1, 0)
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY年MM月DD日"
        ])
        lang_layout.addWidget(self.date_format_combo, 1, 1)
        
        layout.addWidget(lang_group)
        layout.addStretch()
    
    def load_settings(self):
        """加载设置"""
        # 应用程序设置
        self.show_splash_check.setChecked(
            self.config_manager.get_config('ui.show_splash_screen', True)
        )
        self.minimize_to_tray_check.setChecked(
            self.config_manager.get_config('ui.minimize_to_tray', False)
        )
        self.check_updates_check.setChecked(
            self.config_manager.get_config('app.check_updates_on_startup', True)
        )
        self.auto_save_check.setChecked(
            self.config_manager.get_config('app.auto_save_config', True)
        )

        # 界面设置 - 主题映射
        theme_mapping = {
            'default': '默认',
            'dark': '深色',
            'light': '浅色',
            'high_contrast': '高对比度'
        }
        theme_config = self.config_manager.get_config('ui.theme', 'default')
        theme_display = theme_mapping.get(theme_config, '默认')
        index = self.theme_combo.findText(theme_display)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.font_size_spin.setValue(
            self.config_manager.get_config('ui.font_size', 9)
        )
        
        self.transparency_slider.setValue(
            self.config_manager.get_config('ui.window_transparency', 100)
        )
        
        self.show_tooltips_check.setChecked(
            self.config_manager.get_config('ui.show_tooltips', True)
        )
        
        # 语言设置 - 语言映射
        language_mapping = {
            'zh_CN': '简体中文',
            'en_US': 'English',
            'zh_TW': '繁體中文',
            'ja_JP': '日本語'
        }
        language_config = self.config_manager.get_config('ui.language', 'zh_CN')
        language_display = language_mapping.get(language_config, '简体中文')
        index = self.language_combo.findText(language_display)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        date_format = self.config_manager.get_config('ui.date_format', 'YYYY-MM-DD')
        index = self.date_format_combo.findText(date_format)
        if index >= 0:
            self.date_format_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """保存设置"""
        # 应用程序设置
        self.config_manager.set_config('ui.show_splash_screen', self.show_splash_check.isChecked())
        self.config_manager.set_config('ui.minimize_to_tray', self.minimize_to_tray_check.isChecked())
        self.config_manager.set_config('app.check_updates_on_startup', self.check_updates_check.isChecked())
        self.config_manager.set_config('app.auto_save_config', self.auto_save_check.isChecked())

        # 界面设置 - 主题反向映射
        theme_reverse_mapping = {
            '默认': 'default',
            '深色': 'dark',
            '浅色': 'light',
            '高对比度': 'high_contrast'
        }
        theme_display = self.theme_combo.currentText()
        theme_config = theme_reverse_mapping.get(theme_display, 'default')
        self.config_manager.set_config('ui.theme', theme_config)

        self.config_manager.set_config('ui.font_size', self.font_size_spin.value())
        self.config_manager.set_config('ui.window_transparency', self.transparency_slider.value())
        self.config_manager.set_config('ui.show_tooltips', self.show_tooltips_check.isChecked())

        # 语言设置 - 语言反向映射
        language_reverse_mapping = {
            '简体中文': 'zh_CN',
            'English': 'en_US',
            '繁體中文': 'zh_TW',
            '日本語': 'ja_JP'
        }
        language_display = self.language_combo.currentText()
        language_config = language_reverse_mapping.get(language_display, 'zh_CN')
        self.config_manager.set_config('ui.language', language_config)

        self.config_manager.set_config('ui.date_format', self.date_format_combo.currentText())


class SecuritySettingsWidget(QWidget):
    """安全设置控件"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 操作确认设置组
        confirm_group = QGroupBox("操作确认设置")
        confirm_layout = QGridLayout(confirm_group)
        
        # 启用三级确认
        confirm_layout.addWidget(QLabel("启用三级确认:"), 0, 0)
        self.three_level_confirm_check = QCheckBox()
        confirm_layout.addWidget(self.three_level_confirm_check, 0, 1)
        
        # MAC地址修改确认
        confirm_layout.addWidget(QLabel("MAC地址修改确认:"), 1, 0)
        self.mac_modify_confirm_check = QCheckBox()
        confirm_layout.addWidget(self.mac_modify_confirm_check, 1, 1)
        
        # GUID修改确认
        confirm_layout.addWidget(QLabel("GUID修改确认:"), 2, 0)
        self.guid_modify_confirm_check = QCheckBox()
        confirm_layout.addWidget(self.guid_modify_confirm_check, 2, 1)
        
        # 系统恢复确认
        confirm_layout.addWidget(QLabel("系统恢复确认:"), 3, 0)
        self.restore_confirm_check = QCheckBox()
        confirm_layout.addWidget(self.restore_confirm_check, 3, 1)
        
        layout.addWidget(confirm_group)
        
        # 备份设置组
        backup_group = QGroupBox("备份设置")
        backup_layout = QGridLayout(backup_group)
        
        # 自动备份
        backup_layout.addWidget(QLabel("操作前自动备份:"), 0, 0)
        self.auto_backup_check = QCheckBox()
        backup_layout.addWidget(self.auto_backup_check, 0, 1)
        
        # 备份保留天数
        backup_layout.addWidget(QLabel("备份保留天数:"), 1, 0)
        self.backup_retention_spin = QSpinBox()
        self.backup_retention_spin.setRange(1, 365)
        self.backup_retention_spin.setSuffix(" 天")
        backup_layout.addWidget(self.backup_retention_spin, 1, 1)
        
        # 备份压缩
        backup_layout.addWidget(QLabel("压缩备份文件:"), 2, 0)
        self.backup_compression_check = QCheckBox()
        backup_layout.addWidget(self.backup_compression_check, 2, 1)
        
        # 备份加密
        backup_layout.addWidget(QLabel("加密备份文件:"), 3, 0)
        self.backup_encryption_check = QCheckBox()
        backup_layout.addWidget(self.backup_encryption_check, 3, 1)
        
        layout.addWidget(backup_group)
        
        # 日志设置组
        log_group = QGroupBox("日志设置")
        log_layout = QGridLayout(log_group)
        
        # 日志级别
        log_layout.addWidget(QLabel("日志级别:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        log_layout.addWidget(self.log_level_combo, 0, 1)
        
        # 启用审计日志
        log_layout.addWidget(QLabel("启用审计日志:"), 1, 0)
        self.audit_log_check = QCheckBox()
        log_layout.addWidget(self.audit_log_check, 1, 1)
        
        # 日志文件大小限制
        log_layout.addWidget(QLabel("日志文件大小限制:"), 2, 0)
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(1, 100)
        self.log_size_spin.setSuffix(" MB")
        log_layout.addWidget(self.log_size_spin, 2, 1)
        
        layout.addWidget(log_group)
        layout.addStretch()
    
    def load_settings(self):
        """加载设置"""
        # 操作确认设置
        self.three_level_confirm_check.setChecked(
            self.config_manager.get_config('security.three_level_confirmation', True)
        )
        self.mac_modify_confirm_check.setChecked(
            self.config_manager.get_config('security.mac_modification_confirmation', True)
        )
        self.guid_modify_confirm_check.setChecked(
            self.config_manager.get_config('security.guid_modification_confirmation', True)
        )
        self.restore_confirm_check.setChecked(
            self.config_manager.get_config('security.restore_confirmation', True)
        )
        
        # 备份设置
        self.auto_backup_check.setChecked(
            self.config_manager.get_config('backup.auto_backup_before_operation', True)
        )
        self.backup_retention_spin.setValue(
            self.config_manager.get_config('backup.retention_days', 30)
        )
        self.backup_compression_check.setChecked(
            self.config_manager.get_config('backup.compression_enabled', True)
        )
        self.backup_encryption_check.setChecked(
            self.config_manager.get_config('backup.encryption_enabled', False)
        )
        
        # 日志设置
        log_level = self.config_manager.get_config('logging.level', 'INFO')
        index = self.log_level_combo.findText(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        
        self.audit_log_check.setChecked(
            self.config_manager.get_config('logging.audit_enabled', True)
        )
        self.log_size_spin.setValue(
            self.config_manager.get_config('logging.max_file_size_mb', 10)
        )
    
    def save_settings(self):
        """保存设置"""
        # 操作确认设置
        self.config_manager.set_config('security.three_level_confirmation', self.three_level_confirm_check.isChecked())
        self.config_manager.set_config('security.mac_modification_confirmation', self.mac_modify_confirm_check.isChecked())
        self.config_manager.set_config('security.guid_modification_confirmation', self.guid_modify_confirm_check.isChecked())
        self.config_manager.set_config('security.restore_confirmation', self.restore_confirm_check.isChecked())
        
        # 备份设置
        self.config_manager.set_config('backup.auto_backup_before_operation', self.auto_backup_check.isChecked())
        self.config_manager.set_config('backup.retention_days', self.backup_retention_spin.value())
        self.config_manager.set_config('backup.compression_enabled', self.backup_compression_check.isChecked())
        self.config_manager.set_config('backup.encryption_enabled', self.backup_encryption_check.isChecked())
        
        # 日志设置
        self.config_manager.set_config('logging.level', self.log_level_combo.currentText())
        self.config_manager.set_config('logging.audit_enabled', self.audit_log_check.isChecked())
        self.config_manager.set_config('logging.max_file_size_mb', self.log_size_spin.value())


class AdvancedSettingsWidget(QWidget):
    """高级设置控件"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 性能设置组
        perf_group = QGroupBox("性能设置")
        perf_layout = QGridLayout(perf_group)
        
        # 启用缓存
        perf_layout.addWidget(QLabel("启用数据缓存:"), 0, 0)
        self.enable_cache_check = QCheckBox()
        perf_layout.addWidget(self.enable_cache_check, 0, 1)
        
        # 缓存过期时间
        perf_layout.addWidget(QLabel("缓存过期时间:"), 1, 0)
        self.cache_expire_spin = QSpinBox()
        self.cache_expire_spin.setRange(1, 3600)
        self.cache_expire_spin.setSuffix(" 秒")
        perf_layout.addWidget(self.cache_expire_spin, 1, 1)
        
        # 并行查询
        perf_layout.addWidget(QLabel("启用并行查询:"), 2, 0)
        self.parallel_query_check = QCheckBox()
        perf_layout.addWidget(self.parallel_query_check, 2, 1)
        
        # 最大线程数
        perf_layout.addWidget(QLabel("最大线程数:"), 3, 0)
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 16)
        perf_layout.addWidget(self.max_threads_spin, 3, 1)
        
        layout.addWidget(perf_group)
        
        # 开发者设置组
        dev_group = QGroupBox("开发者设置")
        dev_layout = QGridLayout(dev_group)
        
        # 启用调试模式
        dev_layout.addWidget(QLabel("启用调试模式:"), 0, 0)
        self.debug_mode_check = QCheckBox()
        dev_layout.addWidget(self.debug_mode_check, 0, 1)
        
        # 显示内部错误
        dev_layout.addWidget(QLabel("显示内部错误:"), 1, 0)
        self.show_internal_errors_check = QCheckBox()
        dev_layout.addWidget(self.show_internal_errors_check, 1, 1)
        
        # 启用性能监控
        dev_layout.addWidget(QLabel("启用性能监控:"), 2, 0)
        self.performance_monitoring_check = QCheckBox()
        dev_layout.addWidget(self.performance_monitoring_check, 2, 1)
        
        layout.addWidget(dev_group)
        
        # 实验性功能组
        exp_group = QGroupBox("实验性功能")
        exp_layout = QGridLayout(exp_group)
        
        # 启用实验性功能
        exp_layout.addWidget(QLabel("启用实验性功能:"), 0, 0)
        self.experimental_features_check = QCheckBox()
        exp_layout.addWidget(self.experimental_features_check, 0, 1)
        
        # 警告文本
        warning_text = QLabel("⚠️ 实验性功能可能不稳定，仅建议高级用户使用")
        warning_text.setStyleSheet("color: orange; font-style: italic;")
        exp_layout.addWidget(warning_text, 1, 0, 1, 2)
        
        layout.addWidget(exp_group)
        layout.addStretch()
    
    def load_settings(self):
        """加载设置"""
        # 性能设置
        self.enable_cache_check.setChecked(
            self.config_manager.get_config('performance.enable_cache', True)
        )
        self.cache_expire_spin.setValue(
            self.config_manager.get_config('performance.cache_expire_seconds', 300)
        )
        self.parallel_query_check.setChecked(
            self.config_manager.get_config('performance.enable_parallel_query', False)
        )
        self.max_threads_spin.setValue(
            self.config_manager.get_config('performance.max_threads', 4)
        )
        
        # 开发者设置
        self.debug_mode_check.setChecked(
            self.config_manager.get_config('developer.debug_mode', False)
        )
        self.show_internal_errors_check.setChecked(
            self.config_manager.get_config('developer.show_internal_errors', False)
        )
        self.performance_monitoring_check.setChecked(
            self.config_manager.get_config('developer.performance_monitoring', False)
        )
        
        # 实验性功能
        self.experimental_features_check.setChecked(
            self.config_manager.get_config('experimental.enable_features', False)
        )
    
    def save_settings(self):
        """保存设置"""
        # 性能设置
        self.config_manager.set_config('performance.enable_cache', self.enable_cache_check.isChecked())
        self.config_manager.set_config('performance.cache_expire_seconds', self.cache_expire_spin.value())
        self.config_manager.set_config('performance.enable_parallel_query', self.parallel_query_check.isChecked())
        self.config_manager.set_config('performance.max_threads', self.max_threads_spin.value())
        
        # 开发者设置
        self.config_manager.set_config('developer.debug_mode', self.debug_mode_check.isChecked())
        self.config_manager.set_config('developer.show_internal_errors', self.show_internal_errors_check.isChecked())
        self.config_manager.set_config('developer.performance_monitoring', self.performance_monitoring_check.isChecked())
        
        # 实验性功能
        self.config_manager.set_config('experimental.enable_features', self.experimental_features_check.isChecked())


class SettingsDialog(QDialog):
    """设置对话框"""
    
    # 信号定义
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.logger = get_logger("settings_dialog")
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("设置")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 常规设置标签页
        self.general_widget = GeneralSettingsWidget(self.config_manager)
        self.tab_widget.addTab(self.general_widget, "常规")
        
        # 安全设置标签页
        self.security_widget = SecuritySettingsWidget(self.config_manager)
        self.tab_widget.addTab(self.security_widget, "安全")
        
        # 高级设置标签页
        self.advanced_widget = AdvancedSettingsWidget(self.config_manager)
        self.tab_widget.addTab(self.advanced_widget, "高级")
        
        # 按钮组
        button_box = QDialogButtonBox()

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept_settings)
        button_box.addButton(ok_btn, QDialogButtonBox.AcceptRole)

        # 应用按钮
        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(self.apply_settings)
        button_box.addButton(apply_btn, QDialogButtonBox.ApplyRole)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_box.addButton(cancel_btn, QDialogButtonBox.RejectRole)

        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_settings)
        button_box.addButton(reset_btn, QDialogButtonBox.ResetRole)
        
        layout.addWidget(button_box)
        
        # 应用样式
        self.apply_styles()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
        """)
    
    def accept_settings(self):
        """确定设置"""
        self.apply_settings()
        self.accept()
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 保存各个标签页的设置
            self.general_widget.save_settings()
            self.security_widget.save_settings()
            self.advanced_widget.save_settings()
            
            # 保存配置到文件
            self.config_manager.save_config()
            
            # 发出设置更改信号
            self.settings_changed.emit()
            
            self.logger.info("设置已保存")
            QMessageBox.information(self, "设置", "设置已成功保存")
            
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "重置设置",
            "确定要重置所有设置为默认值吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 重置配置管理器
                self.config_manager.reset_to_defaults()
                
                # 重新加载各个标签页的设置
                self.general_widget.load_settings()
                self.security_widget.load_settings()
                self.advanced_widget.load_settings()
                
                self.logger.info("设置已重置为默认值")
                QMessageBox.information(self, "重置完成", "所有设置已重置为默认值")
                
            except Exception as e:
                self.logger.error(f"重置设置失败: {e}")
                QMessageBox.critical(self, "错误", f"重置设置失败: {e}")
