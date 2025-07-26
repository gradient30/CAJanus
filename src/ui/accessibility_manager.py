#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无障碍功能管理器
提供键盘导航、屏幕阅读器支持等无障碍功能
"""

from typing import Dict, List, Optional, Callable
from enum import Enum

from PyQt5.QtWidgets import (
    QWidget, QApplication, QShortcut, QLabel,
    QToolTip, QMessageBox
)
from PyQt5.QtCore import Qt, QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFont, QPalette, QColor

from core.logger import get_logger
from core.i18n_manager import get_i18n_manager


class AccessibilityLevel(Enum):
    """无障碍级别"""
    NONE = "none"           # 无特殊需求
    LOW_VISION = "low_vision"     # 低视力
    HIGH_CONTRAST = "high_contrast"  # 高对比度
    KEYBOARD_ONLY = "keyboard_only"  # 仅键盘操作
    SCREEN_READER = "screen_reader"  # 屏幕阅读器


class AccessibilityManager(QObject):
    """无障碍功能管理器"""
    
    # 信号
    accessibility_changed = pyqtSignal(AccessibilityLevel)
    focus_changed = pyqtSignal(QWidget)
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("accessibility_manager")
        self.i18n = get_i18n_manager()
        
        self.current_level = AccessibilityLevel.NONE
        self.keyboard_shortcuts: Dict[str, QShortcut] = {}
        self.focus_chain: List[QWidget] = []
        self.current_focus_index = 0
        
        # 高对比度颜色方案
        self.high_contrast_palette = self._create_high_contrast_palette()
        
        # 键盘导航定时器
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self._announce_focus)
        
        self._init_keyboard_shortcuts()
    
    def _create_high_contrast_palette(self) -> QPalette:
        """创建高对比度调色板"""
        palette = QPalette()
        
        # 高对比度颜色
        black = QColor(0, 0, 0)
        white = QColor(255, 255, 255)
        yellow = QColor(255, 255, 0)
        blue = QColor(0, 0, 255)
        
        # 设置颜色角色
        palette.setColor(QPalette.Window, black)
        palette.setColor(QPalette.WindowText, white)
        palette.setColor(QPalette.Base, black)
        palette.setColor(QPalette.AlternateBase, QColor(64, 64, 64))
        palette.setColor(QPalette.Text, white)
        palette.setColor(QPalette.Button, QColor(64, 64, 64))
        palette.setColor(QPalette.ButtonText, white)
        palette.setColor(QPalette.Highlight, yellow)
        palette.setColor(QPalette.HighlightedText, black)
        palette.setColor(QPalette.Link, blue)
        palette.setColor(QPalette.LinkVisited, QColor(128, 0, 128))
        
        return palette
    
    def _init_keyboard_shortcuts(self):
        """初始化键盘快捷键"""
        try:
            # 全局快捷键定义
            shortcuts = {
                'help': ('F1', self._show_accessibility_help),
                'next_widget': ('Tab', self._focus_next_widget),
                'prev_widget': ('Shift+Tab', self._focus_previous_widget),
                'activate': ('Space', self._activate_current_widget),
                'context_menu': ('F10', self._show_context_menu),
                'main_menu': ('Alt+F', self._focus_main_menu),
                'escape': ('Escape', self._handle_escape),
                'announce_focus': ('Ctrl+F1', self._announce_current_focus)
            }
            
            for name, (key_sequence, callback) in shortcuts.items():
                shortcut = QShortcut(QKeySequence(key_sequence), QApplication.instance())
                shortcut.activated.connect(callback)
                self.keyboard_shortcuts[name] = shortcut
                
            self.logger.info("键盘快捷键初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化键盘快捷键失败: {e}")
    
    def set_accessibility_level(self, level: AccessibilityLevel):
        """设置无障碍级别"""
        try:
            if level == self.current_level:
                return
            
            old_level = self.current_level
            self.current_level = level
            
            # 应用相应的无障碍设置
            self._apply_accessibility_settings(level)
            
            # 发出信号
            self.accessibility_changed.emit(level)
            
            self.logger.info(f"无障碍级别从 {old_level.value} 切换到 {level.value}")
            
        except Exception as e:
            self.logger.error(f"设置无障碍级别失败: {e}")
    
    def _apply_accessibility_settings(self, level: AccessibilityLevel):
        """应用无障碍设置"""
        try:
            app = QApplication.instance()
            if not app:
                return
            
            if level == AccessibilityLevel.HIGH_CONTRAST:
                # 应用高对比度主题
                app.setPalette(self.high_contrast_palette)
                self._set_high_contrast_fonts()
                
            elif level == AccessibilityLevel.LOW_VISION:
                # 放大字体和界面元素
                self._apply_low_vision_settings()
                
            elif level == AccessibilityLevel.KEYBOARD_ONLY:
                # 启用键盘导航
                self._enable_keyboard_navigation()
                
            elif level == AccessibilityLevel.SCREEN_READER:
                # 启用屏幕阅读器支持
                self._enable_screen_reader_support()
                
            elif level == AccessibilityLevel.NONE:
                # 恢复默认设置
                self._restore_default_settings()
                
        except Exception as e:
            self.logger.error(f"应用无障碍设置失败: {e}")
    
    def _set_high_contrast_fonts(self):
        """设置高对比度字体"""
        try:
            app = QApplication.instance()
            if app:
                font = app.font()
                font.setPointSize(font.pointSize() + 2)  # 增大字体
                font.setBold(True)  # 加粗
                app.setFont(font)
                
        except Exception as e:
            self.logger.error(f"设置高对比度字体失败: {e}")
    
    def _apply_low_vision_settings(self):
        """应用低视力设置"""
        try:
            app = QApplication.instance()
            if app:
                # 放大字体
                font = app.font()
                font.setPointSize(max(12, font.pointSize() + 4))
                app.setFont(font)
                
                # 增加工具提示显示时间
                QToolTip.setFont(QFont(font.family(), font.pointSize() + 2))
                
        except Exception as e:
            self.logger.error(f"应用低视力设置失败: {e}")
    
    def _enable_keyboard_navigation(self):
        """启用键盘导航"""
        try:
            # 启用焦点跟踪
            app = QApplication.instance()
            if app:
                app.focusChanged.connect(self._on_focus_changed)
                
            # 启动焦点公告定时器
            self.focus_timer.start(100)  # 100ms检查一次
            
        except Exception as e:
            self.logger.error(f"启用键盘导航失败: {e}")
    
    def _enable_screen_reader_support(self):
        """启用屏幕阅读器支持"""
        try:
            # 设置可访问性属性
            app = QApplication.instance()
            if app:
                app.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTabletEvents, True)
                
            # 启用键盘导航
            self._enable_keyboard_navigation()
            
        except Exception as e:
            self.logger.error(f"启用屏幕阅读器支持失败: {e}")
    
    def _restore_default_settings(self):
        """恢复默认设置"""
        try:
            app = QApplication.instance()
            if app:
                # 恢复默认调色板
                app.setPalette(app.style().standardPalette())
                
                # 恢复默认字体
                default_font = QFont()
                app.setFont(default_font)
                
                # 停止焦点定时器
                self.focus_timer.stop()
                
        except Exception as e:
            self.logger.error(f"恢复默认设置失败: {e}")
    
    def _on_focus_changed(self, old_widget: QWidget, new_widget: QWidget):
        """焦点变化处理"""
        try:
            if new_widget:
                self.focus_changed.emit(new_widget)
                
                # 如果启用了屏幕阅读器支持，公告焦点变化
                if self.current_level == AccessibilityLevel.SCREEN_READER:
                    self._announce_widget(new_widget)
                    
        except Exception as e:
            self.logger.error(f"处理焦点变化失败: {e}")
    
    def _announce_widget(self, widget: QWidget):
        """公告控件信息（用于屏幕阅读器）"""
        try:
            if not widget:
                return
            
            # 获取控件信息
            widget_type = widget.__class__.__name__
            widget_text = ""
            
            # 尝试获取控件文本
            if hasattr(widget, 'text'):
                widget_text = widget.text()
            elif hasattr(widget, 'windowTitle'):
                widget_text = widget.windowTitle()
            elif hasattr(widget, 'toolTip'):
                widget_text = widget.toolTip()
            
            # 构建公告文本
            announcement = f"{widget_type}"
            if widget_text:
                announcement += f": {widget_text}"
            
            # 这里可以集成实际的屏幕阅读器API
            # 目前使用日志记录
            self.logger.info(f"屏幕阅读器公告: {announcement}")
            
        except Exception as e:
            self.logger.error(f"公告控件信息失败: {e}")
    
    def _show_accessibility_help(self):
        """显示无障碍帮助"""
        try:
            help_text = self.i18n.get_text("accessibility.help.content", 
                                         shortcuts=self._get_shortcuts_text())
            
            QMessageBox.information(
                None,
                self.i18n.get_text("accessibility.help.title"),
                help_text
            )
            
        except Exception as e:
            self.logger.error(f"显示无障碍帮助失败: {e}")
    
    def _get_shortcuts_text(self) -> str:
        """获取快捷键说明文本"""
        shortcuts_info = [
            "F1 - 显示帮助",
            "Tab - 下一个控件",
            "Shift+Tab - 上一个控件",
            "Space - 激活当前控件",
            "F10 - 显示上下文菜单",
            "Alt+F - 主菜单",
            "Escape - 取消/返回",
            "Ctrl+F1 - 公告当前焦点"
        ]
        return "\n".join(shortcuts_info)
    
    def _focus_next_widget(self):
        """焦点移到下一个控件"""
        try:
            app = QApplication.instance()
            if app:
                app.focusNextChild()
        except Exception as e:
            self.logger.error(f"焦点移动失败: {e}")
    
    def _focus_previous_widget(self):
        """焦点移到上一个控件"""
        try:
            app = QApplication.instance()
            if app:
                app.focusPreviousChild()
        except Exception as e:
            self.logger.error(f"焦点移动失败: {e}")
    
    def _activate_current_widget(self):
        """激活当前焦点控件"""
        try:
            app = QApplication.instance()
            if app:
                focused_widget = app.focusWidget()
                if focused_widget:
                    # 模拟点击
                    if hasattr(focused_widget, 'click'):
                        focused_widget.click()
                    elif hasattr(focused_widget, 'toggle'):
                        focused_widget.toggle()
        except Exception as e:
            self.logger.error(f"激活控件失败: {e}")
    
    def _show_context_menu(self):
        """显示上下文菜单"""
        try:
            app = QApplication.instance()
            if app:
                focused_widget = app.focusWidget()
                if focused_widget and hasattr(focused_widget, 'customContextMenuRequested'):
                    # 触发上下文菜单
                    focused_widget.customContextMenuRequested.emit(focused_widget.rect().center())
        except Exception as e:
            self.logger.error(f"显示上下文菜单失败: {e}")
    
    def _focus_main_menu(self):
        """焦点移到主菜单"""
        try:
            # 这里需要根据实际的主窗口实现
            pass
        except Exception as e:
            self.logger.error(f"焦点移到主菜单失败: {e}")
    
    def _handle_escape(self):
        """处理Escape键"""
        try:
            app = QApplication.instance()
            if app:
                focused_widget = app.focusWidget()
                if focused_widget:
                    # 尝试关闭对话框或返回上级
                    parent = focused_widget.parent()
                    while parent:
                        if hasattr(parent, 'close') and hasattr(parent, 'isModal'):
                            if parent.isModal():
                                parent.close()
                                return
                        parent = parent.parent()
        except Exception as e:
            self.logger.error(f"处理Escape键失败: {e}")
    
    def _announce_current_focus(self):
        """公告当前焦点"""
        try:
            app = QApplication.instance()
            if app:
                focused_widget = app.focusWidget()
                if focused_widget:
                    self._announce_widget(focused_widget)
        except Exception as e:
            self.logger.error(f"公告当前焦点失败: {e}")
    
    def _announce_focus(self):
        """定时公告焦点（用于调试）"""
        # 这个方法主要用于开发调试，实际使用时可以禁用
        pass
    
    def set_widget_accessible_name(self, widget: QWidget, name: str):
        """设置控件的无障碍名称"""
        try:
            widget.setAccessibleName(name)
        except Exception as e:
            self.logger.error(f"设置无障碍名称失败: {e}")
    
    def set_widget_accessible_description(self, widget: QWidget, description: str):
        """设置控件的无障碍描述"""
        try:
            widget.setAccessibleDescription(description)
        except Exception as e:
            self.logger.error(f"设置无障碍描述失败: {e}")
    
    def get_current_level(self) -> AccessibilityLevel:
        """获取当前无障碍级别"""
        return self.current_level


# 全局无障碍管理器实例
_accessibility_manager: Optional[AccessibilityManager] = None

def get_accessibility_manager() -> AccessibilityManager:
    """获取全局无障碍管理器实例"""
    global _accessibility_manager
    if _accessibility_manager is None:
        _accessibility_manager = AccessibilityManager()
    return _accessibility_manager
