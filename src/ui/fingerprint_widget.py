#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备指纹管理界面
提供硬件指纹信息的显示、修改和管理功能
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QTabWidget, QTextEdit, QComboBox,
    QMessageBox, QProgressDialog, QHeaderView,
    QFrame, QSplitter, QScrollArea, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.platform_factory import get_platform_factory
from core.logger import get_logger
from core.interfaces import NetworkAdapter, RiskLevel


class FingerprintWorker(QThread):
    """设备指纹信息获取工作线程"""
    
    # 信号定义
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self, platform_factory):
        super().__init__()
        self.platform_factory = platform_factory
        self.logger = get_logger("fingerprint_worker")
    
    def run(self):
        """运行工作线程"""
        try:
            self.progress_updated.emit(10, "正在获取设备指纹管理器...")
            
            # 获取设备指纹管理器
            fingerprint_manager = self.platform_factory.create_fingerprint_manager()
            
            self.progress_updated.emit(30, "正在获取网络适配器信息...")
            
            # 获取网络适配器信息
            adapters = fingerprint_manager.get_network_adapters()
            
            self.progress_updated.emit(50, "正在获取硬件信息...")
            
            # 获取硬件信息
            hardware_info = fingerprint_manager.get_hardware_info()
            
            self.progress_updated.emit(70, "正在获取机器标识...")
            
            # 获取机器GUID
            machine_guid = fingerprint_manager.get_machine_guid()
            
            self.progress_updated.emit(90, "正在获取卷序列号...")
            
            # 获取卷序列号
            volume_serials = fingerprint_manager.get_volume_serial_numbers()
            
            self.progress_updated.emit(100, "数据获取完成")
            
            # 组装数据
            data = {
                'adapters': adapters,
                'hardware_info': hardware_info,
                'machine_guid': machine_guid,
                'volume_serials': volume_serials
            }
            
            self.data_ready.emit(data)
            
        except Exception as e:
            self.logger.error(f"获取设备指纹信息失败: {e}")
            self.error_occurred.emit(str(e))


class NetworkAdapterWidget(QWidget):
    """网络适配器管理控件"""
    
    def __init__(self):
        super().__init__()
        self.adapters = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "适配器名称", "MAC地址", "类型", "状态", "操作"
        ])
        
        # 设置表格属性
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # 创建操作按钮
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_adapters)
        button_layout.addWidget(self.refresh_btn)
        
        self.modify_btn = QPushButton("修改MAC地址")
        self.modify_btn.clicked.connect(self.modify_mac_address)
        button_layout.addWidget(self.modify_btn)
        
        self.restore_btn = QPushButton("恢复原始MAC")
        self.restore_btn.clicked.connect(self.restore_mac_address)
        button_layout.addWidget(self.restore_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def update_adapters(self, adapters: List[NetworkAdapter]):
        """更新适配器列表"""
        self.adapters = adapters
        self.table.setRowCount(len(adapters))
        
        for row, adapter in enumerate(adapters):
            # 适配器名称
            self.table.setItem(row, 0, QTableWidgetItem(adapter.name))
            
            # MAC地址
            mac_item = QTableWidgetItem(adapter.mac_address)
            # TODO: 实现修改状态检查逻辑
            # if adapter.is_modified:
            #     mac_item.setBackground(QColor(255, 255, 0, 100))  # 黄色背景表示已修改
            self.table.setItem(row, 1, mac_item)
            
            # 类型
            self.table.setItem(row, 2, QTableWidgetItem(adapter.adapter_type.value))
            
            # 状态
            status = adapter.status if adapter.status else "未知"
            self.table.setItem(row, 3, QTableWidgetItem(status))
            
            # 操作按钮
            modify_btn = QPushButton("修改")
            modify_btn.clicked.connect(lambda checked, r=row: self.modify_adapter_mac(r))
            self.table.setCellWidget(row, 4, modify_btn)
    
    def refresh_adapters(self):
        """刷新适配器列表"""
        try:
            # 触发父控件重新获取数据
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, 'refresh_all_data'):
                parent_widget = parent_widget.parent()

            if parent_widget and hasattr(parent_widget, 'refresh_all_data'):
                parent_widget.refresh_all_data()
            else:
                QMessageBox.information(self, "提示", "正在刷新网络适配器信息...")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"刷新适配器列表失败: {e}")
    
    def modify_mac_address(self):
        """修改MAC地址"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.modify_adapter_mac(current_row)
    
    def modify_adapter_mac(self, row: int):
        """修改指定适配器的MAC地址"""
        if row < len(self.adapters):
            adapter = self.adapters[row]
            try:
                # 导入MAC地址修改对话框
                from ui.mac_address_dialog import MacAddressDialog

                # 获取平台工厂
                from core.platform_factory import get_platform_factory
                platform_factory = get_platform_factory()

                # 创建并显示对话框
                dialog = MacAddressDialog(adapter, platform_factory, self)
                if dialog.exec_() == QDialog.Accepted:
                    # 修改成功，刷新适配器列表
                    QMessageBox.information(self, "修改完成",
                                          f"适配器 {adapter.name} 的MAC地址修改完成，正在刷新列表...")
                    # 触发父控件刷新数据
                    if hasattr(self.parent(), 'refresh_all_data'):
                        self.parent().refresh_all_data()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开MAC地址修改对话框: {e}")
    
    def restore_mac_address(self):
        """恢复MAC地址"""
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.adapters):
            QMessageBox.information(self, "提示", "请先选择要恢复的网络适配器")
            return

        adapter = self.adapters[current_row]

        # 确认恢复操作
        reply = QMessageBox.question(self, "确认恢复",
                                   f"确定要恢复适配器 '{adapter.name}' 的原始MAC地址吗？\n\n"
                                   f"当前MAC地址: {adapter.mac_address}\n"
                                   f"此操作将恢复到硬件原始MAC地址。",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # 获取平台工厂
                from core.platform_factory import get_platform_factory
                platform_factory = get_platform_factory()

                # 获取设备指纹管理器
                fingerprint_manager = platform_factory.create_fingerprint_manager()

                # 执行恢复操作
                success = fingerprint_manager.restore_original_mac(adapter.adapter_id)

                if success:
                    QMessageBox.information(self, "恢复成功",
                                          f"适配器 '{adapter.name}' 的MAC地址已恢复到原始值。\n"
                                          f"请等待网络适配器重启完成。")

                    # 刷新适配器列表
                    self.refresh_adapters()
                else:
                    QMessageBox.warning(self, "恢复失败",
                                      f"无法恢复适配器 '{adapter.name}' 的MAC地址。\n"
                                      f"请检查权限或网络适配器状态。")

            except Exception as e:
                QMessageBox.critical(self, "恢复失败",
                                   f"恢复MAC地址时发生错误:\n{e}")


class HardwareInfoWidget(QWidget):
    """硬件信息显示控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 机器GUID组
        self.machine_guid_group = self.create_machine_guid_group()
        scroll_layout.addWidget(self.machine_guid_group)
        
        # 卷序列号组
        self.volume_serial_group = self.create_volume_serial_group()
        scroll_layout.addWidget(self.volume_serial_group)
        
        # 硬件信息组
        self.hardware_info_group = self.create_hardware_info_group()
        scroll_layout.addWidget(self.hardware_info_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def create_machine_guid_group(self):
        """创建机器GUID组"""
        group = QGroupBox("机器GUID")
        layout = QGridLayout(group)
        
        # 当前GUID
        layout.addWidget(QLabel("当前GUID:"), 0, 0)
        self.current_guid_edit = QLineEdit()
        self.current_guid_edit.setReadOnly(True)
        layout.addWidget(self.current_guid_edit, 0, 1)
        
        # 新GUID
        layout.addWidget(QLabel("新GUID:"), 1, 0)
        self.new_guid_edit = QLineEdit()
        layout.addWidget(self.new_guid_edit, 1, 1)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("生成新GUID")
        generate_btn.clicked.connect(self.generate_new_guid)
        button_layout.addWidget(generate_btn)
        
        modify_btn = QPushButton("修改GUID")
        modify_btn.clicked.connect(self.modify_guid)
        button_layout.addWidget(modify_btn)
        
        restore_btn = QPushButton("恢复GUID")
        restore_btn.clicked.connect(self.restore_guid)
        button_layout.addWidget(restore_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout, 2, 0, 1, 2)
        
        return group
    
    def create_volume_serial_group(self):
        """创建卷序列号组"""
        group = QGroupBox("卷序列号")
        layout = QVBoxLayout(group)
        
        # 创建表格
        self.volume_table = QTableWidget()
        self.volume_table.setColumnCount(4)
        self.volume_table.setHorizontalHeaderLabels([
            "驱动器", "当前序列号", "新序列号", "操作"
        ])
        
        header = self.volume_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.volume_table)
        
        return group
    
    def create_hardware_info_group(self):
        """创建硬件信息组"""
        group = QGroupBox("硬件信息 (只读)")
        layout = QVBoxLayout(group)
        
        self.hardware_text = QTextEdit()
        self.hardware_text.setReadOnly(True)
        self.hardware_text.setMaximumHeight(200)
        layout.addWidget(self.hardware_text)
        
        return group
    
    def update_hardware_info(self, data: Dict):
        """更新硬件信息"""
        # 更新机器GUID
        machine_guid = data.get('machine_guid', 'N/A')
        self.current_guid_edit.setText(machine_guid)
        
        # 更新卷序列号
        volume_serials = data.get('volume_serials', {})
        self.volume_table.setRowCount(len(volume_serials))
        
        for row, (drive, serial) in enumerate(volume_serials.items()):
            self.volume_table.setItem(row, 0, QTableWidgetItem(drive))
            self.volume_table.setItem(row, 1, QTableWidgetItem(serial))
            
            # 新序列号输入框
            new_serial_edit = QLineEdit()
            self.volume_table.setCellWidget(row, 2, new_serial_edit)
            
            # 修改按钮
            modify_btn = QPushButton("修改")
            modify_btn.clicked.connect(lambda checked, r=row: self.modify_volume_serial(r))
            self.volume_table.setCellWidget(row, 3, modify_btn)
        
        # 更新硬件信息
        hardware_info = data.get('hardware_info', {})
        info_text = ""
        for category, info in hardware_info.items():
            info_text += f"=== {category} ===\n"
            if isinstance(info, dict):
                for key, value in info.items():
                    info_text += f"{key}: {value}\n"
            else:
                info_text += f"{info}\n"
            info_text += "\n"
        
        self.hardware_text.setPlainText(info_text)
    
    def generate_new_guid(self):
        """生成新GUID"""
        import uuid
        new_guid = str(uuid.uuid4()).upper()
        self.new_guid_edit.setText(new_guid)
    
    def modify_guid(self):
        """修改GUID"""
        try:
            # 导入GUID修改对话框
            from ui.guid_modification_dialog import GuidModificationDialog

            # 获取平台工厂
            from core.platform_factory import get_platform_factory
            platform_factory = get_platform_factory()

            # 获取当前GUID
            current_guid = self.current_guid_edit.text().strip()
            if not current_guid:
                QMessageBox.warning(self, "警告", "无法获取当前GUID")
                return

            # 创建并显示对话框
            dialog = GuidModificationDialog(current_guid, platform_factory, self)
            if dialog.exec_() == QDialog.Accepted:
                # 修改成功，刷新硬件信息
                QMessageBox.information(self, "修改完成",
                                      "机器GUID修改完成，请重启系统使更改生效。")
                # 触发父控件刷新数据
                if hasattr(self.parent().parent(), 'refresh_all_data'):
                    self.parent().parent().refresh_all_data()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开GUID修改对话框: {e}")
    
    def restore_guid(self):
        """恢复GUID"""
        try:
            # 获取平台工厂
            from core.platform_factory import get_platform_factory
            platform_factory = get_platform_factory()

            # 检查平台支持
            fingerprint_manager = platform_factory.create_fingerprint_manager()

            # 检查是否支持GUID恢复
            if hasattr(fingerprint_manager, 'get_supported_operations'):
                supported_ops = fingerprint_manager.get_supported_operations()
                if 'restore_original_guid' not in supported_ops:
                    # 检查是否有备份可以恢复
                    from core.config_manager import ConfigManager
                    config_manager = ConfigManager()
                    backup_dir = config_manager.get_backup_directory()

                    # 查找最近的备份文件
                    backup_files = list(backup_dir.glob("backup_*.bak"))
                    if not backup_files:
                        QMessageBox.information(self, "无法恢复",
                                              "当前平台不支持直接恢复GUID，且没有找到可用的备份文件。\n\n"
                                              "建议：\n"
                                              "1. 使用系统备份功能创建备份\n"
                                              "2. 通过备份恢复来还原GUID")
                        return

                    # 提示用户使用备份恢复
                    reply = QMessageBox.question(self, "恢复GUID",
                                               "当前平台不支持直接恢复GUID。\n\n"
                                               "是否要通过系统备份来恢复GUID？\n"
                                               "这将恢复最近一次备份的所有系统设置。",
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        # 跳转到备份恢复功能
                        self.show_backup_restore()
                    return

            # 如果支持直接恢复，执行恢复操作
            current_guid = self.current_guid_label.text()

            # 确认恢复操作
            reply = QMessageBox.question(self, "确认恢复GUID",
                                       f"确定要恢复机器GUID吗？\n\n"
                                       f"当前GUID: {current_guid}\n\n"
                                       f"⚠️ 警告：\n"
                                       f"• 此操作将恢复到系统原始GUID\n"
                                       f"• 可能影响软件许可和系统识别\n"
                                       f"• 建议在操作前创建系统备份\n\n"
                                       f"是否继续？",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 执行恢复操作
                success = fingerprint_manager.restore_original_guid()

                if success:
                    QMessageBox.information(self, "恢复成功",
                                          "机器GUID已恢复到原始值。\n"
                                          "建议重启系统以确保更改完全生效。")

                    # 刷新硬件信息
                    if hasattr(self.parent().parent(), 'refresh_all_data'):
                        self.parent().parent().refresh_all_data()
                else:
                    QMessageBox.warning(self, "恢复失败",
                                      "无法恢复机器GUID。\n"
                                      "请检查权限或系统状态。")

        except Exception as e:
            QMessageBox.critical(self, "恢复失败",
                               f"恢复GUID时发生错误:\n{e}")

    def show_backup_restore(self):
        """显示备份恢复界面"""
        try:
            # 查找主窗口
            main_window = self.window()

            # 如果主窗口有标签页控件，切换到备份管理标签页
            if hasattr(main_window, 'tab_widget'):
                for i in range(main_window.tab_widget.count()):
                    if '备份' in main_window.tab_widget.tabText(i):
                        main_window.tab_widget.setCurrentIndex(i)
                        break

            QMessageBox.information(self, "提示", "已切换到备份管理界面，请使用备份恢复功能。")

        except Exception as e:
            QMessageBox.warning(self, "提示", f"无法切换到备份界面: {e}")
    
    def modify_volume_serial(self, row: int):
        """修改卷序列号"""
        try:
            # 获取驱动器信息
            if row >= self.volume_table.rowCount():
                QMessageBox.warning(self, "错误", "无效的驱动器选择")
                return

            drive_item = self.volume_table.item(row, 0)
            current_serial_item = self.volume_table.item(row, 1)
            new_serial_widget = self.volume_table.cellWidget(row, 2)

            if not drive_item or not current_serial_item or not new_serial_widget:
                QMessageBox.warning(self, "错误", "无法获取驱动器信息")
                return

            drive = drive_item.text()
            current_serial = current_serial_item.text()
            new_serial = new_serial_widget.text().strip()

            if not new_serial:
                QMessageBox.warning(self, "警告", "请输入新的卷序列号")
                return

            # 验证序列号格式（8位十六进制）
            if not self.validate_volume_serial(new_serial):
                QMessageBox.warning(self, "格式错误",
                                  "卷序列号格式不正确。\n"
                                  "请输入8位十六进制数字（如：1234ABCD）")
                return

            # 检查平台支持
            from core.platform_factory import get_platform_factory
            platform_factory = get_platform_factory()
            fingerprint_manager = platform_factory.create_fingerprint_manager()

            # 检查是否支持卷序列号修改
            if hasattr(fingerprint_manager, 'get_supported_operations'):
                supported_ops = fingerprint_manager.get_supported_operations()
                if 'modify_volume_serial' not in supported_ops:
                    unsupported_ops = getattr(fingerprint_manager, 'get_unsupported_operations', lambda: [])()
                    if 'modify_volume_serial' in unsupported_ops:
                        QMessageBox.information(self, "功能不支持",
                                              f"当前平台不支持修改卷序列号。\n\n"
                                              f"支持的平台：Windows\n"
                                              f"当前平台：{platform_factory.get_platform_name()}")
                        return

            # 确认修改操作
            reply = QMessageBox.question(self, "确认修改卷序列号",
                                       f"确定要修改驱动器 {drive} 的卷序列号吗？\n\n"
                                       f"当前序列号: {current_serial}\n"
                                       f"新序列号: {new_serial}\n\n"
                                       f"⚠️ 警告：\n"
                                       f"• 修改卷序列号可能影响软件许可\n"
                                       f"• 某些程序可能依赖于卷序列号\n"
                                       f"• 建议在操作前创建系统备份\n\n"
                                       f"是否继续？",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 执行修改操作
                success = fingerprint_manager.modify_volume_serial(drive, new_serial)

                if success:
                    QMessageBox.information(self, "修改成功",
                                          f"驱动器 {drive} 的卷序列号已修改为 {new_serial}。\n"
                                          f"更改将在下次重启后生效。")

                    # 刷新硬件信息
                    if hasattr(self.parent().parent(), 'refresh_all_data'):
                        self.parent().parent().refresh_all_data()
                else:
                    QMessageBox.warning(self, "修改失败",
                                      f"无法修改驱动器 {drive} 的卷序列号。\n"
                                      f"请检查权限或驱动器状态。")

        except Exception as e:
            QMessageBox.critical(self, "修改失败",
                               f"修改卷序列号时发生错误:\n{e}")

    def validate_volume_serial(self, serial: str) -> bool:
        """验证卷序列号格式"""
        try:
            # 移除可能的分隔符
            serial = serial.replace('-', '').replace(':', '').replace(' ', '')

            # 检查长度（8位十六进制）
            if len(serial) != 8:
                return False

            # 检查是否为有效的十六进制
            int(serial, 16)
            return True

        except ValueError:
            return False


class FingerprintWidget(QWidget):
    """设备指纹管理主控件"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("fingerprint_widget")
        self.platform_factory = None
        self.worker = None
        self.progress_dialog = None
        
        self.init_ui()
        self.init_platform()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 网络适配器标签页
        self.network_widget = NetworkAdapterWidget()
        self.tab_widget.addTab(self.network_widget, "网络适配器")
        
        # 硬件信息标签页
        self.hardware_widget = HardwareInfoWidget()
        self.tab_widget.addTab(self.hardware_widget, "硬件信息")
        
        # 创建刷新按钮
        refresh_layout = QHBoxLayout()
        self.refresh_all_btn = QPushButton("刷新所有信息")
        self.refresh_all_btn.clicked.connect(self.refresh_all_data)
        refresh_layout.addWidget(self.refresh_all_btn)
        refresh_layout.addStretch()
        
        layout.addLayout(refresh_layout)
    
    def init_platform(self):
        """初始化平台工厂"""
        try:
            self.platform_factory = get_platform_factory()
            self.logger.info("平台工厂初始化完成")
            
            # 自动刷新数据
            QTimer.singleShot(1000, self.refresh_all_data)
            
        except Exception as e:
            self.logger.error(f"平台工厂初始化失败: {e}")
            QMessageBox.critical(self, "错误", f"平台初始化失败: {e}")
    
    def refresh_all_data(self):
        """刷新所有数据"""
        if not self.platform_factory:
            QMessageBox.warning(self, "警告", "平台未初始化")
            return
        
        # 创建进度对话框
        self.progress_dialog = QProgressDialog("正在获取设备指纹信息...", "取消", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        
        # 创建工作线程
        self.worker = FingerprintWorker(self.platform_factory)
        self.worker.data_ready.connect(self.on_data_ready)
        self.worker.error_occurred.connect(self.on_error_occurred)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.finished.connect(self.on_worker_finished)
        
        # 连接取消按钮
        self.progress_dialog.canceled.connect(self.cancel_operation)
        
        # 启动线程
        self.worker.start()
    
    def on_data_ready(self, data: Dict):
        """数据准备完成"""
        try:
            # 更新网络适配器
            adapters = data.get('adapters', [])
            self.network_widget.update_adapters(adapters)
            
            # 更新硬件信息
            self.hardware_widget.update_hardware_info(data)
            
            self.logger.info("设备指纹信息更新完成")
            
        except Exception as e:
            self.logger.error(f"数据更新失败: {e}")
            QMessageBox.critical(self, "错误", f"数据更新失败: {e}")
    
    def on_error_occurred(self, error_message: str):
        """处理错误"""
        QMessageBox.critical(self, "错误", f"获取设备指纹信息失败:\n{error_message}")
    
    def on_progress_updated(self, value: int, message: str):
        """更新进度"""
        if self.progress_dialog is not None:
            try:
                self.progress_dialog.setValue(value)
                self.progress_dialog.setLabelText(message)
            except (AttributeError, RuntimeError):
                # 对话框可能已经被删除，忽略错误
                pass
    
    def on_worker_finished(self):
        """工作线程完成"""
        if self.progress_dialog is not None:
            try:
                self.progress_dialog.close()
            except (AttributeError, RuntimeError):
                # 对话框可能已经被删除，忽略错误
                pass
            finally:
                self.progress_dialog = None

        if self.worker is not None:
            try:
                self.worker.deleteLater()
            except (AttributeError, RuntimeError):
                # 线程可能已经被删除，忽略错误
                pass
            finally:
                self.worker = None
    
    def cancel_operation(self):
        """取消操作"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.on_worker_finished()
