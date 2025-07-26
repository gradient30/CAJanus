#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应式布局管理器
支持不同屏幕尺寸和分辨率的自适应布局
"""

import sys
from typing import Dict, List, Tuple, Optional
from enum import Enum

from PyQt5.QtWidgets import (
    QWidget, QLayout, QLayoutItem, QSizePolicy,
    QApplication, QDesktopWidget, QGridLayout,
    QVBoxLayout, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt, QRect, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QScreen

from core.logger import get_logger


class ScreenSize(Enum):
    """屏幕尺寸类型"""
    SMALL = "small"      # < 1366x768
    MEDIUM = "medium"    # 1366x768 - 1920x1080
    LARGE = "large"      # 1920x1080 - 2560x1440
    XLARGE = "xlarge"    # > 2560x1440


class DPIScale(Enum):
    """DPI缩放级别"""
    NORMAL = 1.0    # 96 DPI
    HIGH = 1.25     # 120 DPI
    HIGHER = 1.5    # 144 DPI
    HIGHEST = 2.0   # 192 DPI


class ResponsiveLayoutManager:
    """响应式布局管理器"""
    
    def __init__(self):
        self.logger = get_logger("responsive_layout")
        self.current_screen_size = ScreenSize.MEDIUM
        self.current_dpi_scale = DPIScale.NORMAL
        self.layout_configs = self._init_layout_configs()
        self.widgets_registry: Dict[str, QWidget] = {}
        
        # 监听屏幕变化
        self.screen_change_timer = QTimer()
        self.screen_change_timer.timeout.connect(self._check_screen_changes)
        self.screen_change_timer.start(1000)  # 每秒检查一次
    
    def _init_layout_configs(self) -> Dict[ScreenSize, Dict]:
        """初始化不同屏幕尺寸的布局配置"""
        return {
            ScreenSize.SMALL: {
                'window_size': (1024, 600),
                'tab_position': 'top',
                'splitter_orientation': Qt.Vertical,
                'splitter_sizes': [400, 200],
                'font_size': 8,
                'icon_size': 16,
                'spacing': 4,
                'margins': (5, 5, 5, 5),
                'hide_secondary_panels': True
            },
            ScreenSize.MEDIUM: {
                'window_size': (1200, 800),
                'tab_position': 'top',
                'splitter_orientation': Qt.Vertical,
                'splitter_sizes': [600, 200],
                'font_size': 9,
                'icon_size': 20,
                'spacing': 6,
                'margins': (8, 8, 8, 8),
                'hide_secondary_panels': False
            },
            ScreenSize.LARGE: {
                'window_size': (1400, 900),
                'tab_position': 'top',
                'splitter_orientation': Qt.Vertical,
                'splitter_sizes': [700, 200],
                'font_size': 10,
                'icon_size': 24,
                'spacing': 8,
                'margins': (10, 10, 10, 10),
                'hide_secondary_panels': False
            },
            ScreenSize.XLARGE: {
                'window_size': (1600, 1000),
                'tab_position': 'left',
                'splitter_orientation': Qt.Horizontal,
                'splitter_sizes': [1200, 400],
                'font_size': 11,
                'icon_size': 28,
                'spacing': 10,
                'margins': (12, 12, 12, 12),
                'hide_secondary_panels': False
            }
        }
    
    def detect_screen_size(self) -> ScreenSize:
        """检测当前屏幕尺寸"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                geometry = screen.geometry()
                width, height = geometry.width(), geometry.height()
                
                if width < 1366 or height < 768:
                    return ScreenSize.SMALL
                elif width <= 1920 and height <= 1080:
                    return ScreenSize.MEDIUM
                elif width <= 2560 and height <= 1440:
                    return ScreenSize.LARGE
                else:
                    return ScreenSize.XLARGE
            
            return ScreenSize.MEDIUM
            
        except Exception as e:
            self.logger.error(f"检测屏幕尺寸失败: {e}")
            return ScreenSize.MEDIUM
    
    def detect_dpi_scale(self) -> DPIScale:
        """检测当前DPI缩放"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                dpi = screen.logicalDotsPerInch()
                
                if dpi <= 100:
                    return DPIScale.NORMAL
                elif dpi <= 125:
                    return DPIScale.HIGH
                elif dpi <= 150:
                    return DPIScale.HIGHER
                else:
                    return DPIScale.HIGHEST
            
            return DPIScale.NORMAL
            
        except Exception as e:
            self.logger.error(f"检测DPI缩放失败: {e}")
            return DPIScale.NORMAL
    
    def register_widget(self, name: str, widget: QWidget):
        """注册需要响应式管理的控件"""
        self.widgets_registry[name] = widget
        self.logger.debug(f"注册响应式控件: {name}")
    
    def apply_responsive_layout(self, widget: QWidget):
        """应用响应式布局"""
        try:
            # 更新屏幕信息
            self.current_screen_size = self.detect_screen_size()
            self.current_dpi_scale = self.detect_dpi_scale()
            
            config = self.layout_configs[self.current_screen_size]
            
            # 应用窗口大小
            if hasattr(widget, 'resize'):
                width, height = config['window_size']
                # 根据DPI缩放调整
                width = int(width * self.current_dpi_scale.value)
                height = int(height * self.current_dpi_scale.value)
                widget.resize(width, height)
            
            # 应用字体大小
            self._apply_font_scaling(widget, config)
            
            # 应用间距和边距
            self._apply_spacing_margins(widget, config)
            
            # 应用特定布局调整
            self._apply_layout_adjustments(widget, config)
            
            self.logger.info(f"应用响应式布局: {self.current_screen_size.value}, DPI: {self.current_dpi_scale.value}")
            
        except Exception as e:
            self.logger.error(f"应用响应式布局失败: {e}")
    
    def _apply_font_scaling(self, widget: QWidget, config: Dict):
        """应用字体缩放"""
        try:
            from PyQt5.QtGui import QFont
            
            base_font_size = config['font_size']
            scaled_font_size = int(base_font_size * self.current_dpi_scale.value)
            
            font = widget.font()
            font.setPointSize(scaled_font_size)
            widget.setFont(font)
            
            # 递归应用到子控件
            for child in widget.findChildren(QWidget):
                child_font = child.font()
                child_font.setPointSize(scaled_font_size)
                child.setFont(child_font)
                
        except Exception as e:
            self.logger.error(f"应用字体缩放失败: {e}")
    
    def _apply_spacing_margins(self, widget: QWidget, config: Dict):
        """应用间距和边距"""
        try:
            spacing = int(config['spacing'] * self.current_dpi_scale.value)
            margins = [int(m * self.current_dpi_scale.value) for m in config['margins']]
            
            layout = widget.layout()
            if layout:
                layout.setSpacing(spacing)
                layout.setContentsMargins(*margins)
                
        except Exception as e:
            self.logger.error(f"应用间距边距失败: {e}")
    
    def _apply_layout_adjustments(self, widget: QWidget, config: Dict):
        """应用特定布局调整"""
        try:
            # 处理分割器
            splitters = widget.findChildren(QSplitter)
            for splitter in splitters:
                splitter.setOrientation(config['splitter_orientation'])
                sizes = [int(s * self.current_dpi_scale.value) for s in config['splitter_sizes']]
                splitter.setSizes(sizes)
            
            # 处理标签页位置
            from PyQt5.QtWidgets import QTabWidget
            tab_widgets = widget.findChildren(QTabWidget)
            for tab_widget in tab_widgets:
                if config['tab_position'] == 'left':
                    tab_widget.setTabPosition(QTabWidget.West)
                elif config['tab_position'] == 'right':
                    tab_widget.setTabPosition(QTabWidget.East)
                elif config['tab_position'] == 'bottom':
                    tab_widget.setTabPosition(QTabWidget.South)
                else:
                    tab_widget.setTabPosition(QTabWidget.North)
            
            # 隐藏次要面板（小屏幕）
            if config.get('hide_secondary_panels', False):
                self._hide_secondary_panels(widget)
                
        except Exception as e:
            self.logger.error(f"应用布局调整失败: {e}")
    
    def _hide_secondary_panels(self, widget: QWidget):
        """隐藏次要面板（小屏幕优化）"""
        try:
            # 这里可以根据具体需求隐藏某些面板
            # 例如：工具栏、状态栏、侧边栏等
            pass
        except Exception as e:
            self.logger.error(f"隐藏次要面板失败: {e}")
    
    def _check_screen_changes(self):
        """检查屏幕变化"""
        try:
            new_screen_size = self.detect_screen_size()
            new_dpi_scale = self.detect_dpi_scale()
            
            if (new_screen_size != self.current_screen_size or 
                new_dpi_scale != self.current_dpi_scale):
                
                self.logger.info(f"检测到屏幕变化: {new_screen_size.value}, DPI: {new_dpi_scale.value}")
                
                # 重新应用布局到所有注册的控件
                for name, widget in self.widgets_registry.items():
                    if widget and not widget.isHidden():
                        self.apply_responsive_layout(widget)
                        
        except Exception as e:
            self.logger.error(f"检查屏幕变化失败: {e}")
    
    def get_optimal_window_size(self) -> Tuple[int, int]:
        """获取当前屏幕的最佳窗口大小"""
        config = self.layout_configs[self.current_screen_size]
        width, height = config['window_size']
        
        # 根据DPI缩放调整
        width = int(width * self.current_dpi_scale.value)
        height = int(height * self.current_dpi_scale.value)
        
        return width, height
    
    def get_scaled_size(self, base_size: int) -> int:
        """获取DPI缩放后的尺寸"""
        return int(base_size * self.current_dpi_scale.value)
    
    def is_small_screen(self) -> bool:
        """判断是否为小屏幕"""
        return self.current_screen_size == ScreenSize.SMALL


# 全局响应式布局管理器实例
_responsive_manager: Optional[ResponsiveLayoutManager] = None

def get_responsive_manager() -> ResponsiveLayoutManager:
    """获取全局响应式布局管理器实例"""
    global _responsive_manager
    if _responsive_manager is None:
        _responsive_manager = ResponsiveLayoutManager()
    return _responsive_manager
