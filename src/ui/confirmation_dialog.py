#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三级确认对话框系统
提供标准化的操作确认和风险评估机制
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QGroupBox, QTextEdit,
    QProgressBar, QCheckBox, QFrame, QScrollArea,
    QWidget, QMessageBox
)

# 尝试导入QButtonBox，如果失败则使用替代方案
try:
    from PyQt5.QtWidgets import QDialogButtonBox as QButtonBox
except ImportError:
    try:
        from PyQt5.QtWidgets import QButtonBox
    except ImportError:
        # 如果都无法导入，创建一个简单的替代类
        class QButtonBox:
            AcceptRole = 0
            RejectRole = 1
            HelpRole = 4

            def __init__(self):
                pass

            def addButton(self, button, role):
                pass
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.interfaces import RiskLevel


class ConfirmationLevel(Enum):
    """确认级别枚举"""
    LEVEL_1 = "基础确认"
    LEVEL_2 = "风险确认" 
    LEVEL_3 = "最终确认"


class OperationType(Enum):
    """操作类型枚举"""
    MAC_MODIFICATION = "MAC地址修改"
    GUID_MODIFICATION = "机器GUID修改"
    SYSTEM_RESTORE = "系统恢复"
    REGISTRY_MODIFICATION = "注册表修改"
    NETWORK_RESET = "网络重置"
    BACKUP_DELETION = "备份删除"


class ConfirmationData:
    """确认数据类"""
    
    def __init__(self, operation_type: OperationType, risk_level: RiskLevel):
        self.operation_type = operation_type
        self.risk_level = risk_level
        self.operation_details = {}
        self.warnings = []
        self.requirements = []
        self.consequences = []
        self.recovery_steps = []
        
    def add_detail(self, key: str, value: str):
        """添加操作详情"""
        self.operation_details[key] = value
        
    def add_warning(self, warning: str):
        """添加警告信息"""
        self.warnings.append(warning)
        
    def add_requirement(self, requirement: str):
        """添加操作要求"""
        self.requirements.append(requirement)
        
    def add_consequence(self, consequence: str):
        """添加可能后果"""
        self.consequences.append(consequence)
        
    def add_recovery_step(self, step: str):
        """添加恢复步骤"""
        self.recovery_steps.append(step)


class ConfirmationStepWidget(QWidget):
    """确认步骤控件"""
    
    def __init__(self, level: ConfirmationLevel, data: ConfirmationData):
        super().__init__()
        self.level = level
        self.data = data
        self.confirmed = False
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 步骤标题
        title_layout = QHBoxLayout()
        
        # 步骤图标
        step_number = list(ConfirmationLevel).index(self.level) + 1
        step_icon = QLabel(f"🔸 步骤 {step_number}")
        step_icon.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        title_layout.addWidget(step_icon)
        
        # 步骤名称
        step_title = QLabel(self.level.value)
        step_title.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        title_layout.addWidget(step_title)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 根据确认级别创建不同内容
        if self.level == ConfirmationLevel.LEVEL_1:
            self.create_basic_confirmation(layout)
        elif self.level == ConfirmationLevel.LEVEL_2:
            self.create_risk_confirmation(layout)
        elif self.level == ConfirmationLevel.LEVEL_3:
            self.create_final_confirmation(layout)
    
    def create_basic_confirmation(self, parent_layout):
        """创建基础确认内容"""
        # 操作信息组
        info_group = QGroupBox("操作信息")
        info_layout = QGridLayout(info_group)
        
        # 操作类型
        info_layout.addWidget(QLabel("操作类型:"), 0, 0)
        operation_label = QLabel(self.data.operation_type.value)
        operation_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        info_layout.addWidget(operation_label, 0, 1)
        
        # 风险等级
        info_layout.addWidget(QLabel("风险等级:"), 1, 0)
        risk_label = QLabel(self.data.risk_level.value)
        risk_color = self.get_risk_color(self.data.risk_level)
        risk_label.setStyleSheet(f"color: {risk_color}; font-weight: bold;")
        info_layout.addWidget(risk_label, 1, 1)
        
        # 操作详情
        if self.data.operation_details:
            row = 2
            for key, value in self.data.operation_details.items():
                info_layout.addWidget(QLabel(f"{key}:"), row, 0)
                detail_label = QLabel(str(value))
                detail_label.setFont(QFont("Consolas", 9))
                info_layout.addWidget(detail_label, row, 1)
                row += 1
        
        parent_layout.addWidget(info_group)
        
        # 确认复选框
        self.basic_confirm_check = QCheckBox("我已了解此操作的基本信息")
        self.basic_confirm_check.stateChanged.connect(self.on_confirmation_changed)
        parent_layout.addWidget(self.basic_confirm_check)
    
    def create_risk_confirmation(self, parent_layout):
        """创建风险确认内容"""
        # 警告信息组
        if self.data.warnings:
            warning_group = QGroupBox("⚠️ 重要警告")
            warning_layout = QVBoxLayout(warning_group)
            
            warning_text = QTextEdit()
            warning_text.setReadOnly(True)
            warning_text.setMaximumHeight(120)
            warning_text.setFont(QFont("Microsoft YaHei UI", 9))
            
            warning_content = "\n".join([f"• {warning}" for warning in self.data.warnings])
            warning_text.setPlainText(warning_content)
            warning_text.setStyleSheet("""
                QTextEdit {
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                }
            """)
            
            warning_layout.addWidget(warning_text)
            parent_layout.addWidget(warning_group)
        
        # 操作要求组
        if self.data.requirements:
            req_group = QGroupBox("操作要求")
            req_layout = QVBoxLayout(req_group)
            
            for requirement in self.data.requirements:
                req_check = QCheckBox(requirement)
                req_check.stateChanged.connect(self.on_requirement_changed)
                req_layout.addWidget(req_check)
                
            parent_layout.addWidget(req_group)
        
        # 风险确认复选框
        self.risk_confirm_check = QCheckBox("我已充分了解操作风险并愿意承担后果")
        self.risk_confirm_check.stateChanged.connect(self.on_confirmation_changed)
        parent_layout.addWidget(self.risk_confirm_check)
    
    def create_final_confirmation(self, parent_layout):
        """创建最终确认内容"""
        # 可能后果组
        if self.data.consequences:
            consequence_group = QGroupBox("🚨 可能后果")
            consequence_layout = QVBoxLayout(consequence_group)
            
            consequence_text = QTextEdit()
            consequence_text.setReadOnly(True)
            consequence_text.setMaximumHeight(100)
            consequence_text.setFont(QFont("Microsoft YaHei UI", 9))
            
            consequence_content = "\n".join([f"• {consequence}" for consequence in self.data.consequences])
            consequence_text.setPlainText(consequence_content)
            consequence_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                }
            """)
            
            consequence_layout.addWidget(consequence_text)
            parent_layout.addWidget(consequence_group)
        
        # 恢复方案组
        if self.data.recovery_steps:
            recovery_group = QGroupBox("🔧 恢复方案")
            recovery_layout = QVBoxLayout(recovery_group)
            
            recovery_text = QTextEdit()
            recovery_text.setReadOnly(True)
            recovery_text.setMaximumHeight(100)
            recovery_text.setFont(QFont("Microsoft YaHei UI", 9))
            
            recovery_content = "\n".join([f"{i+1}. {step}" for i, step in enumerate(self.data.recovery_steps)])
            recovery_text.setPlainText(recovery_content)
            recovery_text.setStyleSheet("""
                QTextEdit {
                    background-color: #d1ecf1;
                    border: 1px solid #bee5eb;
                    color: #0c5460;
                }
            """)
            
            recovery_layout.addWidget(recovery_text)
            parent_layout.addWidget(recovery_group)
        
        # 最终确认复选框
        self.final_confirm_check = QCheckBox("我确认要执行此操作，并承担所有风险和后果")
        self.final_confirm_check.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.final_confirm_check.setStyleSheet("color: #dc3545;")
        self.final_confirm_check.stateChanged.connect(self.on_confirmation_changed)
        parent_layout.addWidget(self.final_confirm_check)
    
    def get_risk_color(self, risk_level: RiskLevel) -> str:
        """获取风险等级对应的颜色"""
        color_map = {
            RiskLevel.LOW: "#28a745",      # 绿色
            RiskLevel.MEDIUM: "#ffc107",   # 黄色  
            RiskLevel.HIGH: "#dc3545",     # 红色
            RiskLevel.CRITICAL: "#6f42c1"  # 紫色
        }
        return color_map.get(risk_level, "#6c757d")
    
    def on_confirmation_changed(self):
        """确认状态改变"""
        if self.level == ConfirmationLevel.LEVEL_1:
            self.confirmed = self.basic_confirm_check.isChecked()
        elif self.level == ConfirmationLevel.LEVEL_2:
            self.confirmed = self.risk_confirm_check.isChecked()
        elif self.level == ConfirmationLevel.LEVEL_3:
            self.confirmed = self.final_confirm_check.isChecked()
    
    def on_requirement_changed(self):
        """要求状态改变"""
        # 检查所有要求是否都已满足
        if hasattr(self, 'risk_confirm_check'):
            all_requirements_met = True
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if isinstance(widget, QGroupBox) and widget.title() == "操作要求":
                    for j in range(widget.layout().count()):
                        req_widget = widget.layout().itemAt(j).widget()
                        if isinstance(req_widget, QCheckBox) and not req_widget.isChecked():
                            all_requirements_met = False
                            break
                    break
            
            # 只有所有要求都满足时才能进行风险确认
            self.risk_confirm_check.setEnabled(all_requirements_met)
    
    def is_confirmed(self) -> bool:
        """检查是否已确认"""
        return self.confirmed


class ThreeLevelConfirmationDialog(QDialog):
    """三级确认对话框"""
    
    # 信号定义
    confirmation_completed = pyqtSignal(bool)
    
    def __init__(self, confirmation_data: ConfirmationData, parent=None):
        super().__init__(parent)
        self.confirmation_data = confirmation_data
        self.logger = get_logger("three_level_confirmation")
        self.current_step = 0
        self.step_widgets = []
        
        self.init_ui()
        self.create_steps()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("操作确认")
        self.setFixedSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        # 操作图标
        operation_icon = QLabel("🔐")
        operation_icon.setFont(QFont("Microsoft YaHei UI", 24))
        title_layout.addWidget(operation_icon)
        
        # 标题文本
        title_text = QLabel(f"{self.confirmation_data.operation_type.value} - 操作确认")
        title_text.setFont(QFont("Microsoft YaHei UI", 16, QFont.Bold))
        title_layout.addWidget(title_text)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 进度指示器
        self.create_progress_indicator(layout)
        
        # 步骤内容区域
        self.step_container = QScrollArea()
        self.step_container.setWidgetResizable(True)
        self.step_container.setMinimumHeight(350)
        layout.addWidget(self.step_container)
        
        # 按钮区域
        self.create_buttons(layout)
        
        # 应用样式
        self.apply_styles()
    
    def create_progress_indicator(self, parent_layout):
        """创建进度指示器"""
        progress_group = QGroupBox("确认进度")
        progress_layout = QHBoxLayout(progress_group)
        
        self.progress_labels = []
        for i, level in enumerate(ConfirmationLevel):
            # 步骤标签
            step_label = QLabel(f"{i+1}. {level.value}")
            step_label.setAlignment(Qt.AlignCenter)
            step_label.setMinimumWidth(120)
            step_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                }
            """)
            
            self.progress_labels.append(step_label)
            progress_layout.addWidget(step_label)
            
            # 箭头（除了最后一个）
            if i < len(ConfirmationLevel) - 1:
                arrow_label = QLabel("→")
                arrow_label.setAlignment(Qt.AlignCenter)
                arrow_label.setFont(QFont("Microsoft YaHei UI", 16))
                progress_layout.addWidget(arrow_label)
        
        parent_layout.addWidget(progress_group)
    
    def create_steps(self):
        """创建确认步骤"""
        for level in ConfirmationLevel:
            step_widget = ConfirmationStepWidget(level, self.confirmation_data)
            self.step_widgets.append(step_widget)
        
        # 显示第一个步骤
        self.show_step(0)
    
    def create_buttons(self, parent_layout):
        """创建按钮"""
        button_layout = QHBoxLayout()
        
        # 上一步按钮
        self.prev_btn = QPushButton("上一步")
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)
        button_layout.addWidget(self.prev_btn)
        
        button_layout.addStretch()
        
        # 下一步/完成按钮
        self.next_btn = QPushButton("下一步")
        self.next_btn.clicked.connect(self.next_step)
        self.next_btn.setEnabled(False)
        button_layout.addWidget(self.next_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
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
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f8f8f8;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #888888;
            }
        """)
    
    def show_step(self, step_index: int):
        """显示指定步骤"""
        if 0 <= step_index < len(self.step_widgets):
            self.current_step = step_index
            
            # 更新进度指示器
            self.update_progress_indicator()
            
            # 显示步骤内容
            step_widget = self.step_widgets[step_index]
            self.step_container.setWidget(step_widget)
            
            # 更新按钮状态
            self.update_button_states()
            
            # 监听确认状态变化
            if hasattr(step_widget, 'basic_confirm_check'):
                step_widget.basic_confirm_check.stateChanged.connect(self.update_button_states)
            if hasattr(step_widget, 'risk_confirm_check'):
                step_widget.risk_confirm_check.stateChanged.connect(self.update_button_states)
            if hasattr(step_widget, 'final_confirm_check'):
                step_widget.final_confirm_check.stateChanged.connect(self.update_button_states)
    
    def update_progress_indicator(self):
        """更新进度指示器"""
        for i, label in enumerate(self.progress_labels):
            if i < self.current_step:
                # 已完成的步骤
                label.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        border: 2px solid #28a745;
                        border-radius: 5px;
                        background-color: #d4edda;
                        color: #155724;
                    }
                """)
            elif i == self.current_step:
                # 当前步骤
                label.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        border: 2px solid #007bff;
                        border-radius: 5px;
                        background-color: #cce5ff;
                        color: #004085;
                    }
                """)
            else:
                # 未完成的步骤
                label.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        border: 2px solid #cccccc;
                        border-radius: 5px;
                        background-color: #f8f9fa;
                        color: #6c757d;
                    }
                """)
    
    def update_button_states(self):
        """更新按钮状态"""
        # 上一步按钮
        self.prev_btn.setEnabled(self.current_step > 0)
        
        # 下一步/完成按钮
        current_widget = self.step_widgets[self.current_step]
        is_confirmed = current_widget.is_confirmed()
        
        if self.current_step < len(self.step_widgets) - 1:
            self.next_btn.setText("下一步")
            self.next_btn.setEnabled(is_confirmed)
        else:
            self.next_btn.setText("确认执行")
            self.next_btn.setEnabled(is_confirmed)
            if is_confirmed:
                self.next_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
    
    def previous_step(self):
        """上一步"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def next_step(self):
        """下一步"""
        current_widget = self.step_widgets[self.current_step]
        
        if not current_widget.is_confirmed():
            QMessageBox.warning(self, "警告", "请先完成当前步骤的确认")
            return
        
        if self.current_step < len(self.step_widgets) - 1:
            # 进入下一步
            self.show_step(self.current_step + 1)
        else:
            # 最后一步，执行确认
            self.confirm_operation()
    
    def confirm_operation(self):
        """确认执行操作"""
        # 记录确认日志
        self.logger.info(f"用户确认执行操作: {self.confirmation_data.operation_type.value}")
        
        # 发出确认完成信号
        self.confirmation_completed.emit(True)
        self.accept()
    
    def reject(self):
        """取消操作"""
        self.logger.info(f"用户取消操作: {self.confirmation_data.operation_type.value}")
        self.confirmation_completed.emit(False)
        super().reject()


def create_mac_modification_confirmation(adapter_name: str, old_mac: str, new_mac: str) -> ConfirmationData:
    """创建MAC地址修改确认数据"""
    data = ConfirmationData(OperationType.MAC_MODIFICATION, RiskLevel.MEDIUM)
    
    data.add_detail("适配器名称", adapter_name)
    data.add_detail("当前MAC地址", old_mac)
    data.add_detail("新MAC地址", new_mac)
    
    data.add_warning("MAC地址修改可能导致网络连接中断")
    data.add_warning("某些网络可能有MAC地址白名单限制")
    data.add_warning("企业网络环境可能禁止MAC地址修改")
    
    data.add_requirement("确认具有管理员权限")
    data.add_requirement("确认网卡支持MAC地址修改")
    data.add_requirement("确认已创建系统备份")
    
    data.add_consequence("网络连接可能暂时中断")
    data.add_consequence("需要重新配置网络连接")
    data.add_consequence("某些网络服务可能无法访问")
    
    data.add_recovery_step("恢复原始MAC地址")
    data.add_recovery_step("重启网络适配器")
    data.add_recovery_step("重新配置网络设置")
    data.add_recovery_step("联系网络管理员")
    
    return data


def create_guid_modification_confirmation(old_guid: str, new_guid: str) -> ConfirmationData:
    """创建GUID修改确认数据"""
    data = ConfirmationData(OperationType.GUID_MODIFICATION, RiskLevel.HIGH)
    
    data.add_detail("当前GUID", old_guid)
    data.add_detail("新GUID", new_guid)
    
    data.add_warning("机器GUID修改是高风险操作")
    data.add_warning("可能导致软件许可证失效")
    data.add_warning("Windows激活状态可能受影响")
    data.add_warning("某些应用程序可能无法运行")
    
    data.add_requirement("确认具有管理员权限")
    data.add_requirement("确认已创建完整系统备份")
    data.add_requirement("确认已记录原始GUID")
    data.add_requirement("确认了解所有风险和后果")
    
    data.add_consequence("软件许可证可能失效")
    data.add_consequence("Windows激活可能失效")
    data.add_consequence("应用程序可能无法启动")
    data.add_consequence("系统稳定性可能受影响")
    
    data.add_recovery_step("从备份恢复注册表")
    data.add_recovery_step("恢复原始GUID值")
    data.add_recovery_step("重新激活Windows")
    data.add_recovery_step("重新安装受影响的软件")
    data.add_recovery_step("使用系统还原功能")
    
    return data
