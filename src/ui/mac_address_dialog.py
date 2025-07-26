#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAC地址修改对话框
提供MAC地址修改的专用界面和验证功能
"""

import sys
import re
import random
from pathlib import Path
from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QComboBox, QCheckBox, QTextEdit, QMessageBox,
    QProgressDialog, QFrame, QButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QRegExpValidator, QColor

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.interfaces import NetworkAdapter, RiskLevel


class MacAddressValidator:
    """MAC地址验证器"""
    
    @staticmethod
    def is_valid_mac(mac_address: str) -> bool:
        """验证MAC地址格式是否正确"""
        # 支持多种MAC地址格式
        patterns = [
            r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',  # XX:XX:XX:XX:XX:XX 或 XX-XX-XX-XX-XX-XX
            r'^([0-9A-Fa-f]{2}){6}$',  # XXXXXXXXXXXX
            r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$'  # XXXX.XXXX.XXXX
        ]
        
        for pattern in patterns:
            if re.match(pattern, mac_address):
                return True
        return False
    
    @staticmethod
    def normalize_mac(mac_address: str) -> str:
        """标准化MAC地址格式为XX:XX:XX:XX:XX:XX"""
        # 移除所有分隔符
        clean_mac = re.sub(r'[:-.]', '', mac_address.upper())
        
        # 确保长度为12
        if len(clean_mac) != 12:
            raise ValueError("MAC地址长度不正确")
        
        # 添加冒号分隔符
        return ':'.join([clean_mac[i:i+2] for i in range(0, 12, 2)])
    
    @staticmethod
    def generate_random_mac() -> str:
        """生成随机MAC地址"""
        # 生成随机MAC地址，确保第一个字节的最低位为0（单播地址）
        mac_bytes = [random.randint(0x00, 0xff) for _ in range(6)]
        mac_bytes[0] &= 0xfe  # 确保是单播地址
        mac_bytes[0] |= 0x02  # 设置本地管理位
        
        return ':'.join([f'{b:02x}' for b in mac_bytes]).upper()
    
    @staticmethod
    def get_vendor_info(mac_address: str) -> str:
        """获取MAC地址厂商信息（简化版）"""
        try:
            clean_mac = re.sub(r'[:-.]', '', mac_address.upper())
            oui = clean_mac[:6]
            
            # 简化的厂商信息映射
            vendor_map = {
                '000C29': 'VMware',
                '080027': 'VirtualBox',
                '525400': 'QEMU',
                '001C42': 'Parallels',
                '00155D': 'Microsoft Hyper-V',
                '001DD8': 'Microsoft Corporation',
                '00E04C': 'Realtek',
                '001B21': 'Intel Corporation',
                '00D861': 'Broadcom',
                '001E58': 'WistronNeweb Corporation'
            }
            
            return vendor_map.get(oui, '未知厂商')
            
        except Exception:
            return '未知厂商'


class MacModificationWorker(QThread):
    """MAC地址修改工作线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str)
    modification_completed = pyqtSignal(bool, str)
    
    def __init__(self, adapter: NetworkAdapter, new_mac: str, platform_factory):
        super().__init__()
        self.adapter = adapter
        self.new_mac = new_mac
        self.platform_factory = platform_factory
        self.logger = get_logger("mac_modification_worker")
    
    def run(self):
        """执行MAC地址修改"""
        try:
            self.progress_updated.emit(10, "正在验证新MAC地址...")
            self.msleep(500)
            
            # 验证MAC地址格式
            if not MacAddressValidator.is_valid_mac(self.new_mac):
                raise ValueError("MAC地址格式不正确")
            
            self.progress_updated.emit(30, "正在获取设备指纹管理器...")
            
            # 获取设备指纹管理器
            fingerprint_manager = self.platform_factory.create_fingerprint_manager()
            
            self.progress_updated.emit(50, "正在修改MAC地址...")
            self.msleep(1000)  # 模拟修改过程
            
            # 执行MAC地址修改
            success = fingerprint_manager.modify_mac_address(
                self.adapter.adapter_id, 
                self.new_mac
            )
            
            if not success:
                raise Exception("MAC地址修改失败")
            
            self.progress_updated.emit(80, "正在验证修改结果...")
            self.msleep(500)
            
            # 验证修改结果
            updated_adapters = fingerprint_manager.get_network_adapters()
            modified_adapter = None
            
            for adapter in updated_adapters:
                if adapter.adapter_id == self.adapter.adapter_id:
                    modified_adapter = adapter
                    break
            
            if modified_adapter and modified_adapter.mac_address.upper() == self.new_mac.upper():
                self.progress_updated.emit(100, "MAC地址修改成功")
                self.modification_completed.emit(True, "MAC地址修改成功完成")
            else:
                self.modification_completed.emit(False, "MAC地址修改验证失败")
                
        except Exception as e:
            self.logger.error(f"MAC地址修改失败: {e}")
            self.modification_completed.emit(False, f"MAC地址修改失败: {e}")


class MacAddressDialog(QDialog):
    """MAC地址修改对话框"""
    
    def __init__(self, adapter: NetworkAdapter, platform_factory, parent=None):
        super().__init__(parent)
        self.adapter = adapter
        self.platform_factory = platform_factory
        self.logger = get_logger("mac_address_dialog")
        self.modification_worker = None
        
        self.init_ui()
        self.load_adapter_info()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("修改MAC地址")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 适配器信息组
        self.create_adapter_info_group(layout)
        
        # MAC地址修改组
        self.create_mac_modification_group(layout)
        
        # 风险警告组
        self.create_risk_warning_group(layout)
        
        # 按钮组
        self.create_button_group(layout)
        
        # 应用样式
        self.apply_styles()
    
    def create_adapter_info_group(self, parent_layout):
        """创建适配器信息组"""
        group = QGroupBox("适配器信息")
        layout = QGridLayout(group)
        
        # 适配器名称
        layout.addWidget(QLabel("适配器名称:"), 0, 0)
        self.adapter_name_label = QLabel()
        self.adapter_name_label.setFont(QFont("Microsoft YaHei UI", 9, QFont.Bold))
        layout.addWidget(self.adapter_name_label, 0, 1)
        
        # 当前MAC地址
        layout.addWidget(QLabel("当前MAC地址:"), 1, 0)
        self.current_mac_label = QLabel()
        self.current_mac_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.current_mac_label, 1, 1)
        
        # 厂商信息
        layout.addWidget(QLabel("厂商信息:"), 2, 0)
        self.vendor_label = QLabel()
        layout.addWidget(self.vendor_label, 2, 1)
        
        # 适配器状态
        layout.addWidget(QLabel("适配器状态:"), 3, 0)
        self.status_label = QLabel()
        layout.addWidget(self.status_label, 3, 1)
        
        parent_layout.addWidget(group)
    
    def create_mac_modification_group(self, parent_layout):
        """创建MAC地址修改组"""
        group = QGroupBox("MAC地址修改")
        layout = QVBoxLayout(group)
        
        # 新MAC地址输入
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("新MAC地址:"), 0, 0)
        self.new_mac_edit = QLineEdit()
        self.new_mac_edit.setPlaceholderText("例如: 00:11:22:33:44:55")
        self.new_mac_edit.setFont(QFont("Consolas", 10))
        self.new_mac_edit.textChanged.connect(self.on_mac_text_changed)
        input_layout.addWidget(self.new_mac_edit, 0, 1)
        
        # MAC地址生成按钮
        generate_layout = QHBoxLayout()
        
        self.generate_random_btn = QPushButton("生成随机MAC")
        self.generate_random_btn.clicked.connect(self.generate_random_mac)
        generate_layout.addWidget(self.generate_random_btn)
        
        self.generate_vendor_btn = QPushButton("生成厂商MAC")
        self.generate_vendor_btn.clicked.connect(self.generate_vendor_mac)
        generate_layout.addWidget(self.generate_vendor_btn)
        
        generate_layout.addStretch()
        
        layout.addLayout(input_layout)
        layout.addLayout(generate_layout)
        
        # MAC地址验证状态
        self.validation_label = QLabel()
        self.validation_label.setFont(QFont("Microsoft YaHei UI", 8))
        layout.addWidget(self.validation_label)
        
        # 修改选项
        options_layout = QHBoxLayout()
        
        self.backup_check = QCheckBox("修改前创建备份")
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.backup_check)
        
        self.restart_adapter_check = QCheckBox("修改后重启适配器")
        self.restart_adapter_check.setChecked(True)
        options_layout.addWidget(self.restart_adapter_check)
        
        layout.addLayout(options_layout)
        
        parent_layout.addWidget(group)
    
    def create_risk_warning_group(self, parent_layout):
        """创建风险警告组"""
        group = QGroupBox("⚠️ 风险警告")
        layout = QVBoxLayout(group)
        
        warning_text = QTextEdit()
        warning_text.setReadOnly(True)
        warning_text.setMaximumHeight(120)
        warning_text.setFont(QFont("Microsoft YaHei UI", 9))
        
        warning_content = """
风险等级: 中等

注意事项:
• MAC地址修改可能导致网络连接中断
• 某些网卡不支持MAC地址修改
• 企业网络可能有MAC地址白名单限制
• 修改后可能需要重新配置网络连接
• 建议在测试环境中先进行验证

法律提醒:
• 仅在授权的网络环境中使用此功能
• 遵守相关法律法规和网络使用政策
• 不得用于非法网络活动
        """
        
        warning_text.setPlainText(warning_content.strip())
        warning_text.setStyleSheet("""
            QTextEdit {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
            }
        """)
        
        layout.addWidget(warning_text)
        parent_layout.addWidget(group)
    
    def create_button_group(self, parent_layout):
        """创建按钮组"""
        button_box = QButtonBox()
        
        # 修改按钮
        self.modify_btn = QPushButton("修改MAC地址")
        self.modify_btn.clicked.connect(self.modify_mac_address)
        self.modify_btn.setEnabled(False)
        button_box.addButton(self.modify_btn, QButtonBox.AcceptRole)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_box.addButton(cancel_btn, QButtonBox.RejectRole)
        
        # 帮助按钮
        help_btn = QPushButton("帮助")
        help_btn.clicked.connect(self.show_help)
        button_box.addButton(help_btn, QButtonBox.HelpRole)
        
        parent_layout.addWidget(button_box)
    
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
    
    def load_adapter_info(self):
        """加载适配器信息"""
        self.adapter_name_label.setText(self.adapter.name)
        self.current_mac_label.setText(self.adapter.mac_address)
        
        # 获取厂商信息
        vendor = MacAddressValidator.get_vendor_info(self.adapter.mac_address)
        self.vendor_label.setText(vendor)
        
        # 设置状态
        status = self.adapter.status if self.adapter.status else "未知"
        self.status_label.setText(status)

        # 根据状态设置颜色
        if status.lower() in ['disabled', 'down', 'inactive', '已禁用']:
            self.status_label.setStyleSheet("color: red;")
    
    def on_mac_text_changed(self, text: str):
        """MAC地址文本改变事件"""
        if not text:
            self.validation_label.setText("")
            self.modify_btn.setEnabled(False)
            return
        
        # 验证MAC地址格式
        if MacAddressValidator.is_valid_mac(text):
            try:
                normalized_mac = MacAddressValidator.normalize_mac(text)
                vendor = MacAddressValidator.get_vendor_info(normalized_mac)
                
                self.validation_label.setText(f"✓ 有效的MAC地址 (厂商: {vendor})")
                self.validation_label.setStyleSheet("color: green;")
                self.modify_btn.setEnabled(True)
                
                # 检查是否与当前MAC地址相同
                if normalized_mac.upper() == self.adapter.mac_address.upper():
                    self.validation_label.setText("⚠️ 与当前MAC地址相同")
                    self.validation_label.setStyleSheet("color: orange;")
                    self.modify_btn.setEnabled(False)
                    
            except ValueError as e:
                self.validation_label.setText(f"✗ {e}")
                self.validation_label.setStyleSheet("color: red;")
                self.modify_btn.setEnabled(False)
        else:
            self.validation_label.setText("✗ 无效的MAC地址格式")
            self.validation_label.setStyleSheet("color: red;")
            self.modify_btn.setEnabled(False)
    
    def generate_random_mac(self):
        """生成随机MAC地址"""
        random_mac = MacAddressValidator.generate_random_mac()
        self.new_mac_edit.setText(random_mac)
    
    def generate_vendor_mac(self):
        """生成特定厂商的MAC地址"""
        # 简化版：生成Intel厂商的MAC地址
        intel_oui = "001B21"
        random_suffix = ''.join([f'{random.randint(0, 255):02X}' for _ in range(3)])
        vendor_mac = f"{intel_oui}{random_suffix}"
        
        # 格式化为标准格式
        formatted_mac = ':'.join([vendor_mac[i:i+2] for i in range(0, 12, 2)])
        self.new_mac_edit.setText(formatted_mac)
    
    def modify_mac_address(self):
        """修改MAC地址"""
        new_mac = self.new_mac_edit.text().strip()

        if not new_mac:
            QMessageBox.warning(self, "警告", "请输入新的MAC地址")
            return

        # 检查是否启用三级确认
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()

        if config_manager.get_config('security.three_level_confirmation', True):
            # 使用三级确认对话框
            from ui.confirmation_dialog import (
                ThreeLevelConfirmationDialog,
                create_mac_modification_confirmation
            )

            confirmation_data = create_mac_modification_confirmation(
                self.adapter.name,
                self.adapter.mac_address,
                new_mac
            )

            confirmation_dialog = ThreeLevelConfirmationDialog(confirmation_data, self)
            confirmation_dialog.confirmation_completed.connect(
                lambda confirmed: self.on_confirmation_completed(confirmed, new_mac)
            )

            confirmation_dialog.exec_()
            return
        else:
            # 使用简单确认
            reply = QMessageBox.question(
                self, "确认修改",
                f"确定要将适配器 '{self.adapter.name}' 的MAC地址\n"
                f"从 '{self.adapter.mac_address}' 修改为 '{new_mac}' 吗？\n\n"
                f"此操作可能导致网络连接中断。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.execute_mac_modification(new_mac)

    def on_confirmation_completed(self, confirmed: bool, new_mac: str):
        """三级确认完成处理"""
        if confirmed:
            self.execute_mac_modification(new_mac)

    def execute_mac_modification(self, new_mac: str):
        """执行MAC地址修改"""
        
        # 创建进度对话框
        progress_dialog = QProgressDialog("正在修改MAC地址...", "取消", 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        
        # 启动修改线程
        self.modification_worker = MacModificationWorker(
            self.adapter, new_mac, self.platform_factory
        )
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
            QMessageBox.information(self, "修改成功", message)
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
MAC地址修改帮助

MAC地址格式:
• XX:XX:XX:XX:XX:XX (推荐)
• XX-XX-XX-XX-XX-XX
• XXXXXXXXXXXX
• XXXX.XXXX.XXXX

注意事项:
1. 确保适配器支持MAC地址修改
2. 修改前建议创建系统备份
3. 某些网络可能有MAC地址限制
4. 修改后可能需要重新连接网络

如果修改失败:
1. 检查是否有管理员权限
2. 确认网卡驱动支持MAC修改
3. 尝试重启网络适配器
4. 必要时恢复原始MAC地址
        """
        
        QMessageBox.information(self, "帮助", help_text.strip())
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.modification_worker and self.modification_worker.isRunning():
            reply = QMessageBox.question(
                self, "确认关闭",
                "MAC地址修改正在进行中，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.cancel_modification()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
