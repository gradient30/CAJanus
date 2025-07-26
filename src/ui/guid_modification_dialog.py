#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器GUID修改对话框
提供机器GUID修改的专用界面和验证功能
"""

import sys
import re
import uuid
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QTextEdit, QMessageBox, QProgressDialog,
    QCheckBox, QFrame
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
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger


class GuidValidator:
    """GUID验证器"""
    
    @staticmethod
    def is_valid_guid(guid_string: str) -> bool:
        """验证GUID格式是否正确"""
        # GUID格式: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        pattern = r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$'
        return bool(re.match(pattern, guid_string))
    
    @staticmethod
    def normalize_guid(guid_string: str) -> str:
        """标准化GUID格式"""
        # 移除大括号和空格
        clean_guid = guid_string.strip().strip('{}').upper()
        
        # 验证格式
        if not GuidValidator.is_valid_guid(clean_guid):
            raise ValueError("GUID格式不正确")
        
        return clean_guid
    
    @staticmethod
    def generate_new_guid() -> str:
        """生成新的GUID"""
        return str(uuid.uuid4()).upper()


class GuidModificationWorker(QThread):
    """GUID修改工作线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str)
    modification_completed = pyqtSignal(bool, str)
    
    def __init__(self, new_guid: str, platform_factory):
        super().__init__()
        self.new_guid = new_guid
        self.platform_factory = platform_factory
        self.logger = get_logger("guid_modification_worker")
    
    def run(self):
        """执行GUID修改"""
        try:
            self.progress_updated.emit(10, "正在验证新GUID...")
            self.msleep(500)
            
            # 验证GUID格式
            if not GuidValidator.is_valid_guid(self.new_guid):
                raise ValueError("GUID格式不正确")
            
            self.progress_updated.emit(30, "正在获取设备指纹管理器...")
            
            # 获取设备指纹管理器
            fingerprint_manager = self.platform_factory.create_fingerprint_manager()
            
            self.progress_updated.emit(50, "正在备份当前GUID...")
            self.msleep(500)
            
            # 获取当前GUID作为备份
            current_guid = fingerprint_manager.get_machine_guid()
            self.logger.info(f"当前GUID备份: {current_guid}")
            
            self.progress_updated.emit(70, "正在修改机器GUID...")
            self.msleep(1000)  # 模拟修改过程
            
            # 执行GUID修改
            success = fingerprint_manager.modify_machine_guid(self.new_guid)
            
            if not success:
                raise Exception("机器GUID修改失败")
            
            self.progress_updated.emit(90, "正在验证修改结果...")
            self.msleep(500)
            
            # 验证修改结果
            updated_guid = fingerprint_manager.get_machine_guid()
            
            if updated_guid.upper() == self.new_guid.upper():
                self.progress_updated.emit(100, "机器GUID修改成功")
                self.modification_completed.emit(True, "机器GUID修改成功完成")
            else:
                self.modification_completed.emit(False, "机器GUID修改验证失败")
                
        except Exception as e:
            self.logger.error(f"机器GUID修改失败: {e}")
            self.modification_completed.emit(False, f"机器GUID修改失败: {e}")


class GuidModificationDialog(QDialog):
    """机器GUID修改对话框"""
    
    def __init__(self, current_guid: str, platform_factory, parent=None):
        super().__init__(parent)
        self.current_guid = current_guid
        self.platform_factory = platform_factory
        self.logger = get_logger("guid_modification_dialog")
        self.modification_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("修改机器GUID")
        self.setFixedSize(550, 650)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 当前GUID信息组
        self.create_current_guid_group(layout)
        
        # GUID修改组
        self.create_guid_modification_group(layout)
        
        # 风险警告组
        self.create_risk_warning_group(layout)
        
        # 按钮组
        self.create_button_group(layout)
        
        # 应用样式
        self.apply_styles()
    
    def create_current_guid_group(self, parent_layout):
        """创建当前GUID信息组"""
        group = QGroupBox("当前机器GUID")
        layout = QGridLayout(group)
        
        # 当前GUID
        layout.addWidget(QLabel("当前GUID:"), 0, 0)
        self.current_guid_label = QLabel(self.current_guid)
        self.current_guid_label.setFont(QFont("Consolas", 10))
        self.current_guid_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.current_guid_label, 0, 1)
        
        # 复制按钮
        copy_btn = QPushButton("复制")
        copy_btn.clicked.connect(self.copy_current_guid)
        layout.addWidget(copy_btn, 0, 2)
        
        # GUID信息
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(80)
        info_text.setFont(QFont("Microsoft YaHei UI", 9))
        
        info_content = f"""
机器GUID是Windows系统的唯一标识符，用于：
• 软件许可证验证
• 系统识别和跟踪
• 某些应用程序的设备绑定
        """
        
        info_text.setPlainText(info_content.strip())
        layout.addWidget(info_text, 1, 0, 1, 3)
        
        parent_layout.addWidget(group)
    
    def create_guid_modification_group(self, parent_layout):
        """创建GUID修改组"""
        group = QGroupBox("GUID修改")
        layout = QVBoxLayout(group)
        
        # 新GUID输入
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("新GUID:"), 0, 0)
        self.new_guid_edit = QLineEdit()
        self.new_guid_edit.setPlaceholderText("例如: 12345678-1234-1234-1234-123456789ABC")
        self.new_guid_edit.setFont(QFont("Consolas", 10))
        self.new_guid_edit.textChanged.connect(self.on_guid_text_changed)
        input_layout.addWidget(self.new_guid_edit, 0, 1)
        
        layout.addLayout(input_layout)
        
        # GUID生成按钮
        generate_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成新GUID")
        self.generate_btn.clicked.connect(self.generate_new_guid)
        generate_layout.addWidget(self.generate_btn)
        
        self.paste_btn = QPushButton("粘贴")
        self.paste_btn.clicked.connect(self.paste_guid)
        generate_layout.addWidget(self.paste_btn)
        
        generate_layout.addStretch()
        
        layout.addLayout(generate_layout)
        
        # GUID验证状态
        self.validation_label = QLabel()
        self.validation_label.setFont(QFont("Microsoft YaHei UI", 8))
        layout.addWidget(self.validation_label)
        
        # 修改选项
        options_layout = QVBoxLayout()
        
        self.backup_check = QCheckBox("修改前创建注册表备份")
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.backup_check)
        
        self.restart_warning_check = QCheckBox("我了解修改后需要重启系统")
        self.restart_warning_check.setChecked(False)
        self.restart_warning_check.stateChanged.connect(self.update_modify_button_state)
        options_layout.addWidget(self.restart_warning_check)
        
        layout.addLayout(options_layout)
        
        parent_layout.addWidget(group)
    
    def create_risk_warning_group(self, parent_layout):
        """创建风险警告组"""
        group = QGroupBox("⚠️ 高风险警告")
        layout = QVBoxLayout(group)
        
        warning_text = QTextEdit()
        warning_text.setReadOnly(True)
        warning_text.setMaximumHeight(150)
        warning_text.setFont(QFont("Microsoft YaHei UI", 9))
        
        warning_content = """
风险等级: 高

严重警告:
• 修改机器GUID可能导致软件许可证失效
• 某些应用程序可能无法正常运行
• Windows激活状态可能受到影响
• 系统稳定性可能受到影响
• 修改后必须重启系统才能生效

操作建议:
• 仅在测试环境中进行此操作
• 修改前务必创建完整的系统备份
• 记录原始GUID以便恢复
• 确保了解所有可能的后果

法律提醒:
• 仅在授权的系统上使用此功能
• 不得用于绕过软件许可证限制
• 遵守相关法律法规和软件使用协议
        """
        
        warning_text.setPlainText(warning_content.strip())
        warning_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
        """)
        
        layout.addWidget(warning_text)
        parent_layout.addWidget(group)
    
    def create_button_group(self, parent_layout):
        """创建按钮组"""
        # 使用水平布局替代QButtonBox以避免导入问题
        button_layout = QHBoxLayout()

        # 帮助按钮（左侧）
        help_btn = QPushButton("帮助")
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)

        # 弹性空间
        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # 修改按钮
        self.modify_btn = QPushButton("修改机器GUID")
        self.modify_btn.clicked.connect(self.modify_machine_guid)
        self.modify_btn.setEnabled(False)
        self.modify_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; font-weight: bold; }")
        button_layout.addWidget(self.modify_btn)

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
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f8f8f8;
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
    
    def copy_current_guid(self):
        """复制当前GUID到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_guid)
        QMessageBox.information(self, "复制成功", "当前GUID已复制到剪贴板")
    
    def paste_guid(self):
        """从剪贴板粘贴GUID"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.new_guid_edit.setText(text)
    
    def generate_new_guid(self):
        """生成新GUID"""
        new_guid = GuidValidator.generate_new_guid()
        self.new_guid_edit.setText(new_guid)
    
    def on_guid_text_changed(self, text: str):
        """GUID文本改变事件"""
        if not text:
            self.validation_label.setText("")
            self.update_modify_button_state()
            return
        
        # 验证GUID格式
        try:
            normalized_guid = GuidValidator.normalize_guid(text)
            self.validation_label.setText("✓ 有效的GUID格式")
            self.validation_label.setStyleSheet("color: green;")
            
            # 检查是否与当前GUID相同
            if normalized_guid.upper() == self.current_guid.upper():
                self.validation_label.setText("⚠️ 与当前GUID相同")
                self.validation_label.setStyleSheet("color: orange;")
                
        except ValueError as e:
            self.validation_label.setText(f"✗ {e}")
            self.validation_label.setStyleSheet("color: red;")
        
        self.update_modify_button_state()
    
    def update_modify_button_state(self):
        """更新修改按钮状态"""
        text = self.new_guid_edit.text().strip()
        is_valid_guid = False
        is_different = False
        
        if text:
            try:
                normalized_guid = GuidValidator.normalize_guid(text)
                is_valid_guid = True
                is_different = normalized_guid.upper() != self.current_guid.upper()
            except ValueError:
                pass
        
        # 只有当GUID有效、与当前不同、且用户确认了解风险时才启用按钮
        self.modify_btn.setEnabled(
            is_valid_guid and 
            is_different and 
            self.restart_warning_check.isChecked()
        )
    
    def modify_machine_guid(self):
        """修改机器GUID"""
        new_guid = self.new_guid_edit.text().strip()

        if not new_guid:
            QMessageBox.warning(self, "警告", "请输入新的机器GUID")
            return

        # 检查是否启用三级确认
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()

        if config_manager.get_config('security.three_level_confirmation', True):
            # 使用三级确认对话框
            from ui.confirmation_dialog import (
                ThreeLevelConfirmationDialog,
                create_guid_modification_confirmation
            )

            confirmation_data = create_guid_modification_confirmation(
                self.current_guid,
                new_guid
            )

            confirmation_dialog = ThreeLevelConfirmationDialog(confirmation_data, self)
            confirmation_dialog.confirmation_completed.connect(
                lambda confirmed: self.on_confirmation_completed(confirmed, new_guid)
            )

            confirmation_dialog.exec_()
            return
        else:
            # 使用简单确认
            reply = QMessageBox.critical(
                self, "最终确认",
                f"⚠️ 这是一个高风险操作！\n\n"
                f"确定要将机器GUID从:\n'{self.current_guid}'\n"
                f"修改为:\n'{new_guid}'\n\n"
                f"此操作可能导致:\n"
                f"• 软件许可证失效\n"
                f"• 应用程序无法运行\n"
                f"• 系统激活问题\n\n"
                f"修改后必须重启系统！\n\n"
                f"确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.execute_guid_modification(new_guid)

    def on_confirmation_completed(self, confirmed: bool, new_guid: str):
        """三级确认完成处理"""
        if confirmed:
            self.execute_guid_modification(new_guid)

    def execute_guid_modification(self, new_guid: str):
        """执行GUID修改"""
        
        # 创建进度对话框
        progress_dialog = QProgressDialog("正在修改机器GUID...", "取消", 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        
        # 启动修改线程
        self.modification_worker = GuidModificationWorker(new_guid, self.platform_factory)
        self.modification_worker.progress_updated.connect(progress_dialog.setValue)
        self.modification_worker.progress_updated.connect(
            lambda value, message: progress_dialog.setLabelText(message)
        )
        self.modification_worker.modification_completed.connect(
            lambda success, message: self.on_modification_completed(
                success, message, progress_dialog
            )
        )
        
        # 连接取消按钮
        progress_dialog.canceled.connect(self.cancel_modification)
        
        self.modification_worker.start()
    
    def on_modification_completed(self, success: bool, message: str, progress_dialog):
        """修改完成处理"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self, "修改成功", 
                f"{message}\n\n请立即重启系统以使更改生效！"
            )
            self.accept()  # 关闭对话框
        else:
            QMessageBox.critical(self, "修改失败", message)
        
        if self.modification_worker:
            self.modification_worker.deleteLater()
            self.modification_worker = None
    
    def cancel_modification(self):
        """取消修改操作"""
        if self.modification_worker and self.modification_worker.isRunning():
            self.modification_worker.terminate()
            self.modification_worker.wait()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
机器GUID修改帮助

什么是机器GUID:
机器GUID是Windows系统的唯一标识符，存储在注册表中，
用于软件许可证验证和系统识别。

GUID格式:
标准格式为: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
其中X为十六进制数字(0-9, A-F)

修改风险:
1. 软件许可证可能失效
2. 某些应用程序可能无法运行
3. Windows激活状态可能受影响
4. 系统稳定性可能受影响

安全建议:
1. 仅在测试环境中使用
2. 修改前创建完整系统备份
3. 记录原始GUID以便恢复
4. 确保有系统恢复方案

如果修改失败:
1. 检查是否有管理员权限
2. 确认注册表访问权限
3. 尝试从备份恢复
4. 必要时使用系统还原
        """
        
        QMessageBox.information(self, "帮助", help_text.strip())
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.modification_worker and self.modification_worker.isRunning():
            reply = QMessageBox.question(
                self, "确认关闭",
                "机器GUID修改正在进行中，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.cancel_modification()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
