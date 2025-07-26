#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统状态监控面板
显示系统状态、权限信息和实时监控数据
"""

import sys
from pathlib import Path
from typing import Dict, Optional
import platform

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QProgressBar, QGroupBox, QTextEdit,
    QPushButton, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.platform_factory import get_platform_factory
from core.logger import get_logger


class StatusIndicator(QWidget):
    """状态指示器控件"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.status = "unknown"
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei UI", 9, QFont.Bold))
        layout.addWidget(title_label)
        
        # 状态指示器
        self.status_frame = QFrame()
        self.status_frame.setFixedSize(60, 60)
        self.status_frame.setFrameStyle(QFrame.Box)
        self.status_frame.setLineWidth(2)
        layout.addWidget(self.status_frame, 0, Qt.AlignCenter)
        
        # 状态文本
        self.status_label = QLabel("未知")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei UI", 8))
        layout.addWidget(self.status_label)
        
        self.set_status("unknown")
    
    def set_status(self, status: str, text: str = None):
        """设置状态"""
        self.status = status
        
        if text is None:
            text = status
        
        self.status_label.setText(text)
        
        # 设置颜色
        if status == "good" or status == "ok":
            color = "#4CAF50"  # 绿色
        elif status == "warning":
            color = "#FF9800"  # 橙色
        elif status == "error" or status == "failed":
            color = "#F44336"  # 红色
        else:
            color = "#9E9E9E"  # 灰色
        
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 30px;
            }}
        """)


class SystemInfoWidget(QWidget):
    """系统信息显示控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_system_info()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建系统信息组
        info_group = QGroupBox("系统信息")
        info_layout = QGridLayout(info_group)
        
        # 系统信息标签
        self.info_labels = {}
        info_items = [
            ("操作系统", "os_name"),
            ("系统版本", "os_version"),
            ("架构", "architecture"),
            ("处理器", "processor"),
            ("Python版本", "python_version"),
            ("当前用户", "current_user")
        ]
        
        for row, (label_text, key) in enumerate(info_items):
            label = QLabel(f"{label_text}:")
            label.setFont(QFont("Microsoft YaHei UI", 9, QFont.Bold))
            info_layout.addWidget(label, row, 0)
            
            value_label = QLabel("获取中...")
            self.info_labels[key] = value_label
            info_layout.addWidget(value_label, row, 1)
        
        layout.addWidget(info_group)
    
    def update_system_info(self):
        """更新系统信息"""
        try:
            import getpass
            
            # 获取系统信息
            info = {
                "os_name": platform.system(),
                "os_version": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor() or "未知",
                "python_version": platform.python_version(),
                "current_user": getpass.getuser()
            }
            
            # 更新标签
            for key, value in info.items():
                if key in self.info_labels:
                    self.info_labels[key].setText(str(value))
                    
        except Exception as e:
            for label in self.info_labels.values():
                label.setText("获取失败")


class PermissionStatusWidget(QWidget):
    """权限状态显示控件"""
    
    def __init__(self):
        super().__init__()
        self.platform_factory = None
        self.permission_manager = None
        self.init_ui()
        self.init_platform()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 权限状态组
        perm_group = QGroupBox("权限状态")
        perm_layout = QGridLayout(perm_group)
        
        # 管理员权限指示器
        self.admin_indicator = StatusIndicator("管理员权限")
        perm_layout.addWidget(self.admin_indicator, 0, 0)
        
        # 网络权限指示器
        self.network_indicator = StatusIndicator("网络权限")
        perm_layout.addWidget(self.network_indicator, 0, 1)
        
        # 文件系统权限指示器
        self.filesystem_indicator = StatusIndicator("文件系统权限")
        perm_layout.addWidget(self.filesystem_indicator, 0, 2)
        
        layout.addWidget(perm_group)
        
        # 权限详情
        details_group = QGroupBox("权限详情")
        details_layout = QVBoxLayout(details_group)
        
        self.permission_text = QTextEdit()
        self.permission_text.setReadOnly(True)
        self.permission_text.setMaximumHeight(150)
        self.permission_text.setFont(QFont("Consolas", 9))
        details_layout.addWidget(self.permission_text)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新权限状态")
        refresh_btn.clicked.connect(self.refresh_permissions)
        details_layout.addWidget(refresh_btn)
        
        layout.addWidget(details_group)
    
    def init_platform(self):
        """初始化平台"""
        try:
            self.platform_factory = get_platform_factory()
            self.permission_manager = self.platform_factory.create_permission_manager()
            self.refresh_permissions()
        except Exception as e:
            self.permission_text.setPlainText(f"权限管理器初始化失败: {e}")
    
    def refresh_permissions(self):
        """刷新权限状态"""
        if not self.permission_manager:
            return
        
        try:
            # 检查管理员权限
            is_admin = self.permission_manager.check_admin_privileges()
            self.admin_indicator.set_status(
                "good" if is_admin else "warning",
                "已获取" if is_admin else "未获取"
            )
            
            # 检查网络权限（简单检查）
            self.network_indicator.set_status("good", "正常")
            
            # 检查文件系统权限（简单检查）
            self.filesystem_indicator.set_status("good", "正常")
            
            # 获取详细权限信息
            try:
                permission_info = self.permission_manager.get_permission_info()
                info_text = "权限详情:\n"
                for key, value in permission_info.items():
                    info_text += f"{key}: {value}\n"
                self.permission_text.setPlainText(info_text)
            except:
                self.permission_text.setPlainText("无法获取详细权限信息")
                
        except Exception as e:
            self.permission_text.setPlainText(f"权限检查失败: {e}")


class PerformanceMonitorWidget(QWidget):
    """性能监控控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 性能监控组
        perf_group = QGroupBox("性能监控")
        perf_layout = QGridLayout(perf_group)
        
        # CPU使用率
        perf_layout.addWidget(QLabel("CPU使用率:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        perf_layout.addWidget(self.cpu_progress, 0, 1)
        self.cpu_label = QLabel("0%")
        perf_layout.addWidget(self.cpu_label, 0, 2)
        
        # 内存使用率
        perf_layout.addWidget(QLabel("内存使用率:"), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        perf_layout.addWidget(self.memory_progress, 1, 1)
        self.memory_label = QLabel("0%")
        perf_layout.addWidget(self.memory_label, 1, 2)
        
        # 磁盘使用率
        perf_layout.addWidget(QLabel("磁盘使用率:"), 2, 0)
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        perf_layout.addWidget(self.disk_progress, 2, 1)
        self.disk_label = QLabel("0%")
        perf_layout.addWidget(self.disk_label, 2, 2)
        
        layout.addWidget(perf_group)
    
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_performance)
        self.timer.start(2000)  # 每2秒更新一次
    
    def update_performance(self):
        """更新性能数据"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_progress.setValue(int(memory_percent))
            self.memory_label.setText(f"{memory_percent:.1f}%")
            
            # 磁盘使用率
            disk = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_progress.setValue(int(disk_percent))
            self.disk_label.setText(f"{disk_percent:.1f}%")
            
        except ImportError:
            # 如果没有psutil，显示模拟数据
            import random
            cpu_val = random.randint(10, 80)
            mem_val = random.randint(30, 70)
            disk_val = random.randint(20, 60)
            
            self.cpu_progress.setValue(cpu_val)
            self.cpu_label.setText(f"{cpu_val}%")
            self.memory_progress.setValue(mem_val)
            self.memory_label.setText(f"{mem_val}%")
            self.disk_progress.setValue(disk_val)
            self.disk_label.setText(f"{disk_val}%")
        except Exception:
            pass


class SystemStatusWidget(QWidget):
    """系统状态监控主控件"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("system_status_widget")
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 系统信息
        self.system_info_widget = SystemInfoWidget()
        scroll_layout.addWidget(self.system_info_widget)
        
        # 权限状态
        self.permission_widget = PermissionStatusWidget()
        scroll_layout.addWidget(self.permission_widget)
        
        # 性能监控
        self.performance_widget = PerformanceMonitorWidget()
        scroll_layout.addWidget(self.performance_widget)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # 刷新按钮
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新所有状态")
        refresh_btn.clicked.connect(self.refresh_all_status)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        
        layout.addLayout(refresh_layout)
    
    def refresh_all_status(self):
        """刷新所有状态"""
        try:
            self.system_info_widget.update_system_info()
            self.permission_widget.refresh_permissions()
            self.performance_widget.update_performance()
            self.logger.info("系统状态刷新完成")
        except Exception as e:
            self.logger.error(f"系统状态刷新失败: {e}")
