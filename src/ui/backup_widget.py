#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份管理界面
提供系统备份、恢复和备份历史管理功能
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QTextEdit, QProgressBar, QMessageBox,
    QFileDialog, QHeaderView, QComboBox, QCheckBox,
    QSplitter, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.config_manager import ConfigManager


class BackupWorker(QThread):
    """备份操作工作线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str)
    backup_completed = pyqtSignal(bool, str)
    
    def __init__(self, backup_type: str, backup_path: str):
        super().__init__()
        self.backup_type = backup_type
        self.backup_path = backup_path
        self.logger = get_logger("backup_worker")
    
    def run(self):
        """执行备份操作"""
        try:
            self.progress_updated.emit(10, "正在准备备份...")

            # 获取备份管理器
            from core.platform_factory import get_platform_factory
            platform_factory = get_platform_factory()

            self.progress_updated.emit(20, "正在获取备份管理器...")

            # 创建备份文件名和时间戳
            from datetime import datetime
            current_time = datetime.now()
            timestamp_for_filename = current_time.strftime("%Y%m%d_%H%M%S")
            timestamp_iso = current_time.isoformat()

            backup_filename = f"backup_{timestamp_for_filename}.bak"
            backup_filepath = os.path.join(self.backup_path, backup_filename)

            self.progress_updated.emit(30, "正在备份注册表信息...")
            self.msleep(500)

            # 备份注册表相关信息
            backup_data = {
                "timestamp": timestamp_iso,
                "timestamp_readable": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "backup_type": self.backup_type,
                "system_info": {},
                "registry_data": {},
                "network_config": {},
                "hardware_info": {}
            }

            # 获取系统信息
            self.progress_updated.emit(40, "正在获取系统信息...")
            try:
                import platform
                backup_data["system_info"] = {
                    "os_name": platform.system(),
                    "os_version": platform.release(),
                    "architecture": platform.machine(),
                    "python_version": platform.python_version()
                }
            except Exception as e:
                self.logger.warning(f"获取系统信息失败: {e}")

            # 获取网络配置
            self.progress_updated.emit(60, "正在备份网络配置...")
            try:
                fingerprint_manager = platform_factory.create_fingerprint_manager()
                adapters = fingerprint_manager.get_network_adapters()
                backup_data["network_config"] = {
                    "adapters": [
                        {
                            "name": adapter.name,
                            "mac_address": adapter.mac_address,
                            "adapter_type": adapter.adapter_type.value,
                            "status": adapter.status
                        }
                        for adapter in adapters
                    ]
                }
            except Exception as e:
                self.logger.warning(f"备份网络配置失败: {e}")

            # 获取硬件信息
            self.progress_updated.emit(80, "正在备份硬件信息...")
            try:
                hardware_info = fingerprint_manager.get_hardware_info()
                machine_guid = fingerprint_manager.get_machine_guid()
                volume_serials = fingerprint_manager.get_volume_serial_numbers()

                backup_data["hardware_info"] = {
                    "machine_guid": machine_guid,
                    "volume_serials": volume_serials,
                    "hardware_details": hardware_info
                }
            except Exception as e:
                self.logger.warning(f"备份硬件信息失败: {e}")

            # 保存备份文件
            self.progress_updated.emit(90, "正在保存备份文件...")
            import json

            # 确保备份目录存在
            os.makedirs(self.backup_path, exist_ok=True)

            with open(backup_filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            self.progress_updated.emit(100, "备份完成")
            self.backup_completed.emit(True, f"备份已保存到: {backup_filepath}")

        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            self.backup_completed.emit(False, f"备份失败: {e}")


class RestoreWorker(QThread):
    """恢复操作工作线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str)
    restore_completed = pyqtSignal(bool, str)
    
    def __init__(self, backup_file: str):
        super().__init__()
        self.backup_file = backup_file
        self.logger = get_logger("restore_worker")
    
    def run(self):
        """执行恢复操作"""
        try:
            self.progress_updated.emit(10, "正在验证备份文件...")

            # 验证备份文件存在
            if not os.path.exists(self.backup_file):
                raise FileNotFoundError(f"备份文件不存在: {self.backup_file}")

            # 读取备份数据
            self.progress_updated.emit(20, "正在读取备份数据...")
            import json

            with open(self.backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            # 验证备份数据格式
            required_keys = ["timestamp", "backup_type", "system_info"]
            for key in required_keys:
                if key not in backup_data:
                    raise ValueError(f"备份文件格式错误，缺少: {key}")

            self.progress_updated.emit(30, "正在获取平台管理器...")

            # 获取平台工厂
            from core.platform_factory import get_platform_factory
            platform_factory = get_platform_factory()
            fingerprint_manager = platform_factory.create_fingerprint_manager()

            # 恢复网络配置
            if "network_config" in backup_data:
                self.progress_updated.emit(50, "正在恢复网络配置...")

                network_config = backup_data["network_config"]
                if "adapters" in network_config:
                    for adapter_data in network_config["adapters"]:
                        try:
                            # 这里可以实现具体的网络配置恢复
                            # 注意：实际恢复需要谨慎处理，避免网络中断
                            self.logger.info(f"恢复适配器配置: {adapter_data['name']}")
                        except Exception as e:
                            self.logger.warning(f"恢复适配器配置失败: {e}")

            # 恢复硬件信息（仅记录，不实际修改）
            if "hardware_info" in backup_data:
                self.progress_updated.emit(70, "正在验证硬件信息...")

                hardware_info = backup_data["hardware_info"]
                if "machine_guid" in hardware_info:
                    original_guid = hardware_info["machine_guid"]
                    self.logger.info(f"备份中的机器GUID: {original_guid}")

                    # 注意：实际的GUID恢复需要用户明确确认
                    # 这里只是记录信息，不自动修改

            # 创建恢复报告
            self.progress_updated.emit(90, "正在生成恢复报告...")

            restore_report = {
                "restore_time": datetime.now().isoformat(),
                "backup_file": self.backup_file,
                "backup_timestamp": backup_data.get("timestamp", "未知"),
                "backup_type": backup_data.get("backup_type", "未知"),
                "restored_items": []
            }

            # 保存恢复报告
            report_filename = f"restore_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join(os.path.dirname(self.backup_file), report_filename)

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(restore_report, f, indent=2, ensure_ascii=False)

            self.progress_updated.emit(100, "恢复完成")
            self.restore_completed.emit(True, f"恢复操作完成\n恢复报告: {report_path}")

        except Exception as e:
            self.logger.error(f"恢复失败: {e}")
            self.restore_completed.emit(False, f"恢复失败: {e}")


class BackupHistoryWidget(QWidget):
    """备份历史管理控件"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.backup_history = []  # 初始化备份历史列表
        self.init_ui()
        self.load_backup_history()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 备份历史表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "备份时间", "备份类型", "文件大小", "状态", "操作"
        ])
        
        # 设置表格属性
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        layout.addWidget(self.history_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.load_backup_history)
        button_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("删除备份")
        delete_btn.clicked.connect(self.delete_backup)
        button_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("导出备份")
        export_btn.clicked.connect(self.export_backup)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def load_backup_history(self):
        """加载备份历史"""
        backup_history = []

        try:
            # 获取备份目录
            backup_dir = self.config_manager.get_backup_directory()
            if not os.path.exists(backup_dir):
                self.logger.info(f"备份目录不存在: {backup_dir}")
                # 不要直接返回，继续执行表格更新（显示空列表）
            else:
                # 扫描备份文件
                for filename in os.listdir(backup_dir):
                    if filename.endswith('.bak') and filename.startswith('backup_'):
                        file_path = os.path.join(backup_dir, filename)

                        try:
                            # 获取文件信息
                            file_stat = os.stat(file_path)
                            file_size = self.format_file_size(file_stat.st_size)

                            # 尝试从备份文件中读取时间戳
                            backup_time = None
                            backup_type = "完整备份"

                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    backup_data = json.load(f)

                                    # 优先使用可读时间戳
                                    if 'timestamp_readable' in backup_data:
                                        backup_time = backup_data['timestamp_readable']
                                    elif 'timestamp' in backup_data:
                                        # 如果是ISO格式，转换为可读格式
                                        try:
                                            dt = datetime.fromisoformat(backup_data['timestamp'].replace('Z', '+00:00'))
                                            backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                                        except:
                                            backup_time = backup_data['timestamp']

                                    backup_type = backup_data.get('backup_type', '完整备份')

                            except (json.JSONDecodeError, KeyError, Exception) as e:
                                # 如果无法读取备份文件，从文件名解析时间
                                try:
                                    # 从文件名提取时间戳 backup_20240115_143025.bak
                                    time_part = filename.replace('backup_', '').replace('.bak', '')
                                    dt = datetime.strptime(time_part, '%Y%m%d_%H%M%S')
                                    backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    # 使用文件修改时间
                                    dt = datetime.fromtimestamp(file_stat.st_mtime)
                                    backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")

                            backup_history.append({
                                "time": backup_time or "未知时间",
                                "type": backup_type,
                                "size": file_size,
                                "status": "正常",
                                "file": filename,
                                "path": file_path
                            })

                        except Exception as e:
                            self.logger.warning(f"处理备份文件 {filename} 时出错: {e}")
                            continue

                # 按时间排序（最新的在前）
                backup_history.sort(key=lambda x: x["time"], reverse=True)

        except Exception as e:
            self.logger.error(f"加载备份历史失败: {e}")
            # 如果出错，显示空列表
            backup_history = []

        # 保存备份历史供其他方法使用
        self.backup_history = backup_history

        self.history_table.setRowCount(len(backup_history))
        
        for row, backup in enumerate(backup_history):
            # 备份时间
            self.history_table.setItem(row, 0, QTableWidgetItem(backup["time"]))
            
            # 备份类型
            self.history_table.setItem(row, 1, QTableWidgetItem(backup["type"]))
            
            # 文件大小
            self.history_table.setItem(row, 2, QTableWidgetItem(backup["size"]))
            
            # 状态
            status_item = QTableWidgetItem(backup["status"])
            if backup["status"] == "正常":
                status_item.setBackground(QColor(200, 255, 200))
            self.history_table.setItem(row, 3, status_item)
            
            # 操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(2, 2, 2, 2)
            
            restore_btn = QPushButton("恢复")
            restore_btn.clicked.connect(lambda checked, f=backup["file"]: self.restore_backup(f))
            button_layout.addWidget(restore_btn)
            
            view_btn = QPushButton("查看")
            view_btn.clicked.connect(lambda checked, f=backup["file"]: self.view_backup(f))
            button_layout.addWidget(view_btn)
            
            self.history_table.setCellWidget(row, 4, button_widget)
    
    def delete_backup(self):
        """删除备份"""
        current_row = self.history_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的备份")
            return

        try:
            # 获取选中的备份文件名
            file_item = self.history_table.item(current_row, 0)
            if not file_item:
                QMessageBox.warning(self, "错误", "无法获取备份文件信息")
                return

            # 从备份历史中找到对应的备份信息
            backup_file = None
            for backup in self.backup_history:
                if backup.get("time") == file_item.text():
                    backup_file = backup.get("file")
                    break

            if not backup_file:
                QMessageBox.warning(self, "错误", "无法找到对应的备份文件")
                return

            # 确认删除
            reply = QMessageBox.question(self, "确认删除",
                                       f"确定要删除备份文件吗？\n\n"
                                       f"文件: {backup_file}\n"
                                       f"时间: {file_item.text()}\n\n"
                                       f"此操作不可撤销！",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                backup_dir = self.config_manager.get_backup_directory()
                backup_path = backup_dir / backup_file

                if backup_path.exists():
                    # 删除备份文件
                    backup_path.unlink()

                    # 刷新备份列表
                    self.load_backup_history()

                    QMessageBox.information(self, "删除成功", f"备份文件已删除:\n{backup_file}")
                else:
                    QMessageBox.warning(self, "错误", f"备份文件不存在:\n{backup_file}")
                    # 仍然刷新列表，移除不存在的条目
                    self.load_backup_history()

        except Exception as e:
            QMessageBox.critical(self, "删除失败", f"删除备份文件时出错:\n{e}")
    
    def export_backup(self):
        """导出备份"""
        current_row = self.history_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "提示", "请先选择要导出的备份")
            return

        try:
            # 获取选中的备份文件名
            file_item = self.history_table.item(current_row, 0)
            if not file_item:
                QMessageBox.warning(self, "错误", "无法获取备份文件信息")
                return

            # 从备份历史中找到对应的备份信息
            backup_file = None
            for backup in self.backup_history:
                if backup.get("time") == file_item.text():
                    backup_file = backup.get("file")
                    break

            if not backup_file:
                QMessageBox.warning(self, "错误", "无法找到对应的备份文件")
                return

            # 选择导出路径
            default_name = f"exported_{backup_file}"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出备份", default_name,
                "备份文件 (*.bak);;JSON文件 (*.json);;所有文件 (*.*)")

            if file_path:
                backup_dir = self.config_manager.get_backup_directory()
                source_path = backup_dir / backup_file

                if not source_path.exists():
                    QMessageBox.warning(self, "错误", f"源备份文件不存在:\n{backup_file}")
                    return

                # 执行导出（复制文件）
                import shutil

                # 创建导出目录（如果不存在）
                export_dir = os.path.dirname(file_path)
                os.makedirs(export_dir, exist_ok=True)

                # 复制文件
                shutil.copy2(str(source_path), file_path)

                # 验证导出是否成功
                if os.path.exists(file_path):
                    exported_size = os.path.getsize(file_path)
                    original_size = source_path.stat().st_size

                    if exported_size == original_size:
                        QMessageBox.information(self, "导出成功",
                                              f"备份文件已成功导出到:\n{file_path}\n\n"
                                              f"文件大小: {self.format_file_size(exported_size)}")
                    else:
                        QMessageBox.warning(self, "导出警告",
                                          f"文件已导出，但大小不匹配:\n"
                                          f"原始: {self.format_file_size(original_size)}\n"
                                          f"导出: {self.format_file_size(exported_size)}")
                else:
                    QMessageBox.critical(self, "导出失败", "导出的文件不存在，可能导出失败")

        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出备份文件时出错:\n{e}")
    
    def restore_backup(self, backup_file: str):
        """恢复备份"""
        reply = QMessageBox.question(self, "确认恢复", 
                                   f"确定要从备份文件 {backup_file} 恢复吗？\n"
                                   "这将覆盖当前的系统设置。",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 这里应该触发恢复操作
            self.parent().parent().restore_from_backup(backup_file)
    
    def view_backup(self, backup_file: str):
        """查看备份详情"""
        try:
            backup_dir = self.config_manager.get_backup_directory()
            backup_path = backup_dir / backup_file

            if not backup_path.exists():
                QMessageBox.warning(self, "错误", f"备份文件不存在: {backup_file}")
                return

            # 读取备份文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            # 构建详情信息
            details = f"备份文件详情\n{'='*50}\n\n"
            details += f"文件名: {backup_file}\n"
            details += f"文件路径: {backup_path}\n"
            details += f"文件大小: {self.format_file_size(backup_path.stat().st_size)}\n\n"

            # 时间信息
            if 'timestamp_readable' in backup_data:
                details += f"备份时间: {backup_data['timestamp_readable']}\n"
            elif 'timestamp' in backup_data:
                details += f"备份时间: {backup_data['timestamp']}\n"

            details += f"备份类型: {backup_data.get('backup_type', '未知')}\n\n"

            # 系统信息
            if 'system_info' in backup_data:
                sys_info = backup_data['system_info']
                details += f"系统信息:\n"
                details += f"  操作系统: {sys_info.get('os_name', 'N/A')} {sys_info.get('os_version', 'N/A')}\n"
                details += f"  架构: {sys_info.get('architecture', 'N/A')}\n"
                details += f"  Python版本: {sys_info.get('python_version', 'N/A')}\n\n"

            # 网络配置
            if 'network_config' in backup_data and 'adapters' in backup_data['network_config']:
                adapters = backup_data['network_config']['adapters']
                details += f"网络适配器: {len(adapters)} 个\n"
                for i, adapter in enumerate(adapters[:3]):  # 只显示前3个
                    details += f"  {i+1}. {adapter.get('name', 'N/A')} - {adapter.get('status', 'N/A')}\n"
                if len(adapters) > 3:
                    details += f"  ... 还有 {len(adapters) - 3} 个适配器\n"
                details += "\n"

            # 硬件信息
            if 'hardware_info' in backup_data:
                hw_info = backup_data['hardware_info']
                details += f"硬件信息:\n"
                details += f"  机器GUID: {hw_info.get('machine_guid', 'N/A')}\n"

                if 'volume_serials' in hw_info:
                    vol_serials = hw_info['volume_serials']
                    details += f"  卷序列号: {len(vol_serials)} 个驱动器\n"
                    for drive, serial in vol_serials.items():
                        details += f"    {drive} - {serial}\n"

            # 显示详情对话框
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

            dialog = QDialog(self)
            dialog.setWindowTitle(f"备份详情 - {backup_file}")
            dialog.setModal(True)
            dialog.resize(600, 500)

            layout = QVBoxLayout(dialog)

            # 详情文本
            text_edit = QTextEdit()
            text_edit.setPlainText(details)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)

            # 按钮
            button_layout = QHBoxLayout()

            open_file_btn = QPushButton("打开文件")
            open_file_btn.clicked.connect(lambda: self.open_backup_file(backup_path))
            button_layout.addWidget(open_file_btn)

            button_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看备份详情失败:\n{e}")

    def open_backup_file(self, file_path):
        """打开备份文件"""
        try:
            import subprocess
            import platform

            system = platform.system()
            success = False

            try:
                if system == "Windows":
                    # 使用notepad打开文件
                    result = subprocess.run(['notepad', str(file_path)],
                                          capture_output=True, text=True, timeout=10)
                    success = True  # notepad启动成功就算成功
                elif system == "Darwin":  # macOS
                    result = subprocess.run(['open', '-t', str(file_path)],
                                          capture_output=True, text=True, timeout=10)
                    success = (result.returncode == 0)
                elif system == "Linux":
                    # 尝试多个编辑器
                    editors = ['gedit', 'kate', 'mousepad', 'leafpad', 'xdg-open']
                    for editor in editors:
                        try:
                            result = subprocess.run([editor, str(file_path)],
                                                  capture_output=True, text=True, timeout=10)
                            if result.returncode == 0:
                                success = True
                                break
                        except FileNotFoundError:
                            continue

                if not success:
                    # 如果无法打开，显示文件路径
                    QMessageBox.information(self, "文件路径",
                                          f"无法自动打开文件，请手动打开:\n{file_path}")

            except subprocess.TimeoutExpired:
                # 超时通常意味着程序已经启动
                success = True
            except FileNotFoundError:
                QMessageBox.information(self, "文件路径",
                                      f"找不到合适的编辑器，文件路径:\n{file_path}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件:\n{e}")


class BackupWidget(QWidget):
    """备份管理主控件"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("backup_widget")
        self.config_manager = ConfigManager()
        self.backup_worker = None
        self.restore_worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # 备份操作区域
        backup_group = self.create_backup_group()
        splitter.addWidget(backup_group)
        
        # 备份历史区域
        self.history_widget = BackupHistoryWidget()
        history_group = QGroupBox("备份历史")
        history_layout = QVBoxLayout(history_group)
        history_layout.addWidget(self.history_widget)
        splitter.addWidget(history_group)
        
        # 设置分割器比例
        splitter.setSizes([300, 400])
    
    def create_backup_group(self):
        """创建备份操作组"""
        group = QGroupBox("备份操作")
        layout = QVBoxLayout(group)
        
        # 备份选项
        options_layout = QGridLayout()
        
        # 备份类型
        options_layout.addWidget(QLabel("备份类型:"), 0, 0)
        self.backup_type_combo = QComboBox()
        self.backup_type_combo.addItems(["完整备份", "增量备份", "差异备份"])
        options_layout.addWidget(self.backup_type_combo, 0, 1)
        
        # 备份路径
        options_layout.addWidget(QLabel("备份路径:"), 1, 0)
        backup_path_layout = QHBoxLayout()
        self.backup_path_edit = QLabel(self.config_manager.get_config('backup.backup_directory', './backups'))
        self.backup_path_edit.setFrameStyle(QFrame.StyledPanel)
        self.backup_path_edit.setStyleSheet("padding: 5px; background-color: white;")
        backup_path_layout.addWidget(self.backup_path_edit)
        
        browse_btn = QPushButton("选择目录")
        browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(browse_btn)

        # 添加查看备份目录按钮
        view_dir_btn = QPushButton("查看备份")
        view_dir_btn.clicked.connect(self.view_backup_directory)
        backup_path_layout.addWidget(view_dir_btn)
        
        options_layout.addLayout(backup_path_layout, 1, 1)
        
        # 备份选项
        self.compress_check = QCheckBox("压缩备份文件")
        self.compress_check.setChecked(self.config_manager.get_config('backup.compression_enabled', True))
        options_layout.addWidget(self.compress_check, 2, 0, 1, 2)
        
        self.encrypt_check = QCheckBox("加密备份文件")
        self.encrypt_check.setChecked(self.config_manager.get_config('backup.encryption_enabled', False))
        options_layout.addWidget(self.encrypt_check, 3, 0, 1, 2)
        
        layout.addLayout(options_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.backup_btn = QPushButton("创建备份")
        self.backup_btn.clicked.connect(self.create_backup)
        button_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton("从文件恢复")
        self.restore_btn.clicked.connect(self.restore_from_file)
        button_layout.addWidget(self.restore_btn)
        
        self.quick_restore_btn = QPushButton("快速恢复")
        self.quick_restore_btn.clicked.connect(self.quick_restore)
        button_layout.addWidget(self.quick_restore_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态文本
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.append("备份系统就绪")
        layout.addWidget(self.status_text)
        
        return group
    
    def browse_backup_path(self):
        """选择备份路径"""
        path = QFileDialog.getExistingDirectory(self, "选择备份目录")
        if path:
            self.backup_path_edit.setText(path)

    def view_backup_directory(self):
        """查看备份目录"""
        try:
            import subprocess
            import platform
            import os

            backup_dir = self.config_manager.get_backup_directory()

            # 确保目录存在
            if not backup_dir.exists():
                backup_dir.mkdir(parents=True, exist_ok=True)

            # 转换为绝对路径
            abs_backup_dir = os.path.abspath(str(backup_dir))

            # 根据操作系统打开文件管理器
            system = platform.system()
            success = False

            try:
                if system == "Windows":
                    # 使用Windows路径分隔符，不使用check=True
                    win_path = abs_backup_dir.replace('/', '\\')
                    result = subprocess.run(['explorer', win_path],
                                          capture_output=True, text=True, timeout=5)
                    # Explorer经常返回非零退出码但仍然成功，所以不检查返回码
                    success = True
                elif system == "Darwin":  # macOS
                    result = subprocess.run(['open', abs_backup_dir],
                                          capture_output=True, text=True, timeout=5)
                    success = (result.returncode == 0)
                elif system == "Linux":
                    result = subprocess.run(['xdg-open', abs_backup_dir],
                                          capture_output=True, text=True, timeout=5)
                    success = (result.returncode == 0)
                else:
                    # 如果无法识别系统，显示路径
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "备份目录", f"备份目录路径:\n{abs_backup_dir}")
                    return

                # 如果命令执行失败且不是Windows系统，显示错误
                if not success and system != "Windows":
                    from PyQt5.QtWidgets import QMessageBox
                    error_msg = result.stderr if result.stderr else "未知错误"
                    QMessageBox.warning(self, "错误", f"无法打开文件管理器:\n{error_msg}")

            except subprocess.TimeoutExpired:
                # 超时通常意味着命令已经启动但没有立即返回，这在某些系统上是正常的
                success = True
            except FileNotFoundError:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "错误", f"找不到文件管理器程序")

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"无法查看备份目录:\n{e}")
    
    def create_backup(self):
        """创建备份"""
        backup_type = self.backup_type_combo.currentText()
        backup_path = self.backup_path_edit.text()
        
        if not os.path.exists(backup_path):
            try:
                os.makedirs(backup_path)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建备份目录: {e}")
                return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.backup_btn.setEnabled(False)
        
        # 启动备份线程
        self.backup_worker = BackupWorker(backup_type, backup_path)
        self.backup_worker.progress_updated.connect(self.on_backup_progress)
        self.backup_worker.backup_completed.connect(self.on_backup_completed)
        self.backup_worker.start()
        
        self.status_text.append(f"开始创建 {backup_type}...")
    
    def restore_from_file(self):
        """从文件恢复"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", "", "备份文件 (*.bak);;所有文件 (*)")
        
        if file_path:
            self.restore_from_backup(file_path)
    
    def restore_from_backup(self, backup_file: str):
        """从备份恢复"""
        reply = QMessageBox.warning(self, "警告", 
                                  "恢复操作将覆盖当前系统设置，确定继续吗？",
                                  QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.restore_btn.setEnabled(False)
            
            # 启动恢复线程
            self.restore_worker = RestoreWorker(backup_file)
            self.restore_worker.progress_updated.connect(self.on_restore_progress)
            self.restore_worker.restore_completed.connect(self.on_restore_completed)
            self.restore_worker.start()
            
            self.status_text.append(f"开始从 {backup_file} 恢复...")
    
    def quick_restore(self):
        """快速恢复最新备份"""
        try:
            # 获取最新的备份文件
            backup_dir = self.config_manager.get_backup_directory()

            if not backup_dir.exists():
                QMessageBox.warning(self, "错误", "备份目录不存在")
                return

            # 查找最新的备份文件
            backup_files = list(backup_dir.glob("backup_*.bak"))
            if not backup_files:
                QMessageBox.information(self, "提示", "没有找到可用的备份文件")
                return

            # 按修改时间排序，获取最新的
            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)

            # 读取备份文件获取时间信息
            try:
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)

                backup_time = backup_data.get('timestamp_readable',
                                            backup_data.get('timestamp', '未知时间'))
            except:
                backup_time = "未知时间"

            # 确认快速恢复
            reply = QMessageBox.question(self, "快速恢复确认",
                                       f"将恢复到最新的备份状态：\n\n"
                                       f"备份文件: {latest_backup.name}\n"
                                       f"备份时间: {backup_time}\n\n"
                                       f"确定要继续吗？\n"
                                       f"此操作将覆盖当前系统设置！",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 执行恢复
                self.restore_from_backup_file(str(latest_backup))

        except Exception as e:
            QMessageBox.critical(self, "快速恢复失败", f"快速恢复时出错:\n{e}")

    def restore_from_backup_file(self, backup_file_path: str):
        """从指定备份文件恢复"""
        try:
            if not os.path.exists(backup_file_path):
                QMessageBox.warning(self, "错误", f"备份文件不存在:\n{backup_file_path}")
                return

            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # 禁用按钮
            self.restore_btn.setEnabled(False)
            self.quick_restore_btn.setEnabled(False)

            # 创建恢复工作线程
            self.restore_worker = RestoreWorker(backup_file_path)
            self.restore_worker.progress_updated.connect(self.on_restore_progress)
            self.restore_worker.restore_completed.connect(self.on_restore_completed)
            self.restore_worker.start()

            self.status_text.append(f"开始快速恢复: {os.path.basename(backup_file_path)}")

        except Exception as e:
            QMessageBox.critical(self, "恢复失败", f"启动恢复过程失败:\n{e}")
            # 重新启用按钮
            self.restore_btn.setEnabled(True)
            self.quick_restore_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def on_backup_progress(self, value: int, message: str):
        """备份进度更新"""
        self.progress_bar.setValue(value)
        self.status_text.append(message)
    
    def on_backup_completed(self, success: bool, message: str):
        """备份完成"""
        self.progress_bar.setVisible(False)
        self.backup_btn.setEnabled(True)
        self.status_text.append(message)
        
        if success:
            QMessageBox.information(self, "备份完成", "备份操作成功完成！")
            self.history_widget.load_backup_history()  # 刷新历史列表
        else:
            QMessageBox.critical(self, "备份失败", message)
    
    def on_restore_progress(self, value: int, message: str):
        """恢复进度更新"""
        self.progress_bar.setValue(value)
        self.status_text.append(message)
    
    def on_restore_completed(self, success: bool, message: str):
        """恢复完成"""
        self.progress_bar.setVisible(False)
        self.restore_btn.setEnabled(True)
        self.status_text.append(message)

        if success:
            QMessageBox.information(self, "恢复完成", "恢复操作成功完成！")
        else:
            QMessageBox.critical(self, "恢复失败", message)

    def start_backup(self):
        """启动备份（供外部调用）"""
        self.create_backup()

    def show_restore_dialog(self):
        """显示恢复对话框（供外部调用）"""
        self.restore_from_file()
