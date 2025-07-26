#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
设备指纹识别与修改工具的主界面
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QStatusBar, QToolBar,
    QAction, QLabel, QMessageBox, QSplitter,
    QTextEdit, QProgressBar, QDialog, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.platform_factory import get_platform_factory
from core.logger import get_logger


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号定义
    status_changed = pyqtSignal(str)
    operation_completed = pyqtSignal(str, bool)
    
    def __init__(self):
        super().__init__()
        
        # 初始化组件
        self.logger = get_logger("main_window")
        self.config_manager = ConfigManager()
        self.platform_factory = None
        
        # UI组件
        self.central_widget = None
        self.tab_widget = None
        self.status_bar = None
        self.log_widget = None
        self.progress_bar = None
        
        # 初始化UI
        self.init_ui()
        self.init_platform()
        self.setup_connections()
        
        self.logger.info("主窗口初始化完成")
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(self.config_manager.get_config('app.name', '设备指纹识别与修改工具'))
        
        # 设置窗口大小和位置
        width, height = self.config_manager.get_window_size()
        self.resize(width, height)
        self.center_window()
        
        # 设置窗口图标（如果有的话）
        self.set_window_icon()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建中央部件
        self.create_central_widget()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 应用样式
        self.apply_styles()
    
    def center_window(self):
        """将窗口居中显示"""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
    
    def set_window_icon(self):
        """设置窗口图标"""
        # 尝试加载图标文件
        icon_paths = [
            "resources/icons/app_icon.png",
            "resources/icons/janus.ico",
            "assets/icon.png"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建配置
        new_action = QAction('新建配置(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('创建新的配置文件')
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        # 打开配置
        open_action = QAction('打开配置(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('打开现有配置文件')
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        # 保存配置
        save_action = QAction('保存配置(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('保存当前配置')
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出应用程序')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        # 系统信息
        sysinfo_action = QAction('系统信息(&I)', self)
        sysinfo_action.setStatusTip('查看系统信息')
        sysinfo_action.triggered.connect(self.show_system_info)
        tools_menu.addAction(sysinfo_action)
        
        # 权限检查
        permission_action = QAction('权限检查(&P)', self)
        permission_action.setStatusTip('检查当前权限状态')
        permission_action.triggered.connect(self.check_permissions)
        tools_menu.addAction(permission_action)
        
        tools_menu.addSeparator()
        
        # 设置
        settings_action = QAction('设置(&S)', self)
        settings_action.setStatusTip('打开设置对话框')
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 使用手册
        manual_action = QAction('使用手册(&M)', self)
        manual_action.setStatusTip('查看使用手册')
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于本软件')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = self.addToolBar('主工具栏')
        toolbar.setMovable(False)
        
        # 刷新按钮
        refresh_action = QAction('刷新', self)
        refresh_action.setStatusTip('刷新系统信息')
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # 备份按钮
        backup_action = QAction('备份', self)
        backup_action.setStatusTip('创建系统备份')
        backup_action.triggered.connect(self.create_backup)
        toolbar.addAction(backup_action)
        
        # 恢复按钮
        restore_action = QAction('恢复', self)
        restore_action.setStatusTip('从备份恢复')
        restore_action.triggered.connect(self.restore_backup)
        toolbar.addAction(restore_action)
    
    def create_central_widget(self):
        """创建中央部件"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(self.central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)
        
        # 创建日志显示区域
        self.create_log_widget()
        splitter.addWidget(self.log_widget)
        
        # 设置分割器比例
        splitter.setSizes([600, 200])
        
        # 创建各个标签页
        self.create_tabs()
    
    def create_log_widget(self):
        """创建日志显示控件"""
        self.log_widget = QTextEdit()
        self.log_widget.setMaximumHeight(200)
        self.log_widget.setReadOnly(True)
        self.log_widget.setFont(QFont("Consolas", 9))
        self.log_widget.append("=== 设备指纹识别与修改工具 ===")
        self.log_widget.append("系统启动中...")
    
    def create_tabs(self):
        """创建标签页"""
        try:
            # 导入功能模块
            from ui.system_status_widget import SystemStatusWidget
            from ui.fingerprint_widget import FingerprintWidget
            from ui.backup_widget import BackupWidget
            from ui.education_widget import EducationWidget

            # 系统状态标签页
            self.system_status_widget = SystemStatusWidget()
            self.tab_widget.addTab(self.system_status_widget, "系统状态")

            # 设备指纹标签页
            self.fingerprint_widget = FingerprintWidget()
            self.tab_widget.addTab(self.fingerprint_widget, "设备指纹")

            # 备份管理标签页
            self.backup_widget = BackupWidget()
            self.tab_widget.addTab(self.backup_widget, "备份管理")

            # 教育功能标签页
            self.education_widget = EducationWidget()
            self.tab_widget.addTab(self.education_widget, "教育功能")

            self.log_widget.append("所有功能模块加载完成")

        except Exception as e:
            self.logger.error(f"标签页创建失败: {e}")
            # 如果加载失败，显示错误信息
            error_label = QLabel(f"功能模块加载失败: {e}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 12px;")
            self.tab_widget.addTab(error_label, "错误")
            self.log_widget.append(f"功能模块加载失败: {e}")
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 平台信息
        platform_label = QLabel("平台: 检测中...")
        self.status_bar.addPermanentWidget(platform_label)
        self.platform_label = platform_label
    
    def apply_styles(self):
        """应用样式表"""
        # 基础样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QStatusBar {
                background-color: #f8f8f8;
                border-top: 1px solid #d0d0d0;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #404040;
            }
        """)
    
    def init_platform(self):
        """初始化平台工厂"""
        try:
            self.platform_factory = get_platform_factory()
            platform_name = self.platform_factory.current_platform
            self.platform_label.setText(f"平台: {platform_name}")
            self.log_widget.append(f"平台检测完成: {platform_name}")
        except Exception as e:
            self.logger.error(f"平台初始化失败: {e}")
            self.platform_label.setText("平台: 未知")
            self.log_widget.append(f"平台初始化失败: {e}")
    
    def setup_connections(self):
        """设置信号连接"""
        self.status_changed.connect(self.update_status)
        self.operation_completed.connect(self.on_operation_completed)
    
    # 菜单动作处理方法
    def new_config(self):
        """新建配置"""
        try:
            reply = QMessageBox.question(self, '新建配置',
                                       '确定要创建新的配置文件吗？\n当前未保存的更改将丢失。',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 重置配置管理器到默认状态
                self.config_manager.reset_to_defaults()
                self.log_widget.append("已创建新的配置文件")
                self.status_changed.emit("新配置已创建")

                # 刷新界面
                self.refresh_data()
            else:
                self.log_widget.append("取消创建新配置")

        except Exception as e:
            self.logger.error(f"创建新配置失败: {e}")
            QMessageBox.critical(self, "错误", f"创建新配置失败:\n{e}")

    def open_config(self):
        """打开配置"""
        try:
            from PyQt5.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getOpenFileName(
                self, '打开配置文件', '',
                'YAML配置文件 (*.yaml *.yml);;JSON配置文件 (*.json);;所有文件 (*.*)'
            )

            if file_path:
                # 加载配置文件
                success = self.config_manager.load_from_file(file_path)
                if success:
                    self.log_widget.append(f"已加载配置文件: {file_path}")
                    self.status_changed.emit("配置文件已加载")

                    # 刷新界面
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "警告", "配置文件加载失败，请检查文件格式")
            else:
                self.log_widget.append("取消打开配置文件")

        except Exception as e:
            self.logger.error(f"打开配置文件失败: {e}")
            QMessageBox.critical(self, "错误", f"打开配置文件失败:\n{e}")

    def save_config(self):
        """保存配置"""
        try:
            from PyQt5.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self, '保存配置文件', 'config.yaml',
                'YAML配置文件 (*.yaml *.yml);;JSON配置文件 (*.json);;所有文件 (*.*)'
            )

            if file_path:
                # 保存配置文件
                success = self.config_manager.save_to_file(file_path)
                if success:
                    self.log_widget.append(f"配置已保存到: {file_path}")
                    self.status_changed.emit("配置文件已保存")
                else:
                    QMessageBox.warning(self, "警告", "配置文件保存失败")
            else:
                self.log_widget.append("取消保存配置文件")

        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            QMessageBox.critical(self, "错误", f"保存配置文件失败:\n{e}")
    
    def show_system_info(self):
        """显示系统信息"""
        try:
            from ui.system_info_dialog import SystemInfoDialog

            dialog = SystemInfoDialog(self)
            dialog.exec_()

            self.log_widget.append("系统信息对话框已显示")

        except ImportError:
            # 如果没有专门的系统信息对话框，创建一个简单的
            self.show_simple_system_info()
        except Exception as e:
            self.logger.error(f"显示系统信息失败: {e}")
            QMessageBox.critical(self, "错误", f"显示系统信息失败:\n{e}")

    def show_simple_system_info(self):
        """显示简单的系统信息"""
        try:
            import platform
            import sys
            from PyQt5.QtCore import QT_VERSION_STR

            info_text = f"""系统信息:

操作系统: {platform.system()} {platform.release()}
架构: {platform.machine()}
处理器: {platform.processor()}
Python版本: {sys.version}
PyQt5版本: {QT_VERSION_STR}
平台: {self.platform_factory.current_platform if self.platform_factory else '未知'}

内存信息:
{self.get_memory_info()}

磁盘信息:
{self.get_disk_info()}
"""

            QMessageBox.information(self, "系统信息", info_text)
            self.log_widget.append("系统信息已显示")

        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            QMessageBox.warning(self, "警告", f"获取系统信息失败:\n{e}")

    def get_memory_info(self):
        """获取内存信息"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return f"总内存: {memory.total // (1024**3)} GB\n可用内存: {memory.available // (1024**3)} GB\n使用率: {memory.percent}%"
        except ImportError:
            return "需要安装psutil库来显示内存信息"
        except Exception as e:
            return f"获取内存信息失败: {e}"

    def get_disk_info(self):
        """获取磁盘信息"""
        try:
            import psutil
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(f"{partition.device}: {usage.total // (1024**3)} GB (使用率: {usage.percent}%)")
                except:
                    disk_info.append(f"{partition.device}: 无法访问")
            return "\n".join(disk_info)
        except ImportError:
            return "需要安装psutil库来显示磁盘信息"
        except Exception as e:
            return f"获取磁盘信息失败: {e}"

    def check_permissions(self):
        """检查权限"""
        try:
            if not self.platform_factory:
                QMessageBox.warning(self, "警告", "平台未初始化，无法检查权限")
                return

            # 获取权限管理器
            permission_manager = self.platform_factory.create_permission_manager()

            # 检查管理员权限
            is_admin = permission_manager.check_admin_privileges()

            # 获取详细权限信息
            permission_info = permission_manager.get_permission_info()

            # 构建权限报告
            report = f"""权限检查报告:

管理员权限: {'✓ 已获取' if is_admin else '✗ 未获取'}

详细权限信息:
"""

            for key, value in permission_info.items():
                report += f"{key}: {value}\n"

            # 添加权限建议
            if not is_admin:
                report += "\n建议: 以管理员身份运行程序以获得完整功能"

            QMessageBox.information(self, "权限检查", report)
            self.log_widget.append("权限检查完成")

        except Exception as e:
            self.logger.error(f"权限检查失败: {e}")
            QMessageBox.critical(self, "错误", f"权限检查失败:\n{e}")
    
    def show_settings(self):
        """显示设置"""
        try:
            from ui.settings_dialog import SettingsDialog

            dialog = SettingsDialog(self)
            dialog.settings_changed.connect(self.on_settings_changed)

            if dialog.exec_() == QDialog.Accepted:
                self.log_widget.append("设置已更新")
            else:
                self.log_widget.append("设置已取消")

        except Exception as e:
            self.logger.error(f"无法打开设置对话框: {e}")
            self.log_widget.append(f"设置对话框打开失败: {e}")

    def on_settings_changed(self):
        """设置更改处理"""
        self.log_widget.append("应用程序设置已更改，某些设置可能需要重启后生效")
        self.status_changed.emit("设置已更新")
    
    def show_manual(self):
        """显示使用手册"""
        try:
            from ui.help_system import HelpSystemDialog

            # 创建帮助系统对话框
            help_dialog = HelpSystemDialog(self)
            help_dialog.show()  # 使用show()而不是exec_()，允许非模态显示

            self.log_widget.append("帮助系统已打开")

        except Exception as e:
            self.logger.error(f"无法打开帮助系统: {e}")
            self.log_widget.append(f"帮助系统打开失败: {e}")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         f"{self.config_manager.get_config('app.name')}\n"
                         f"版本: {self.config_manager.get_config('app.version')}\n"
                         f"高级教学与安全研究平台")
    
    # 工具栏动作处理方法
    def refresh_data(self):
        """刷新数据"""
        self.log_widget.append("正在刷新系统数据...")
        try:
            # 刷新系统状态
            if hasattr(self, 'system_status_widget'):
                self.system_status_widget.refresh_all_status()

            # 刷新设备指纹信息
            if hasattr(self, 'fingerprint_widget'):
                self.fingerprint_widget.refresh_all_data()

            self.log_widget.append("系统数据刷新完成")
            self.status_changed.emit("数据刷新完成")

        except Exception as e:
            self.logger.error(f"数据刷新失败: {e}")
            self.log_widget.append(f"数据刷新失败: {e}")

    def create_backup(self):
        """创建备份"""
        try:
            # 切换到备份管理标签页
            if hasattr(self, 'backup_widget'):
                # 找到备份管理标签页的索引
                for i in range(self.tab_widget.count()):
                    if self.tab_widget.tabText(i) == "备份管理":
                        self.tab_widget.setCurrentIndex(i)
                        break

                # 触发备份创建
                self.backup_widget.start_backup()
                self.log_widget.append("已切换到备份管理页面并开始备份")
                self.status_changed.emit("正在创建备份...")
            else:
                QMessageBox.information(self, "提示", "请使用备份管理标签页来创建备份")

        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            QMessageBox.critical(self, "错误", f"创建备份失败:\n{e}")

    def restore_backup(self):
        """恢复备份"""
        try:
            # 切换到备份管理标签页
            if hasattr(self, 'backup_widget'):
                # 找到备份管理标签页的索引
                for i in range(self.tab_widget.count()):
                    if self.tab_widget.tabText(i) == "备份管理":
                        self.tab_widget.setCurrentIndex(i)
                        break

                # 触发备份恢复对话框
                self.backup_widget.show_restore_dialog()
                self.log_widget.append("已切换到备份管理页面并打开恢复对话框")
                self.status_changed.emit("准备恢复备份...")
            else:
                QMessageBox.information(self, "提示", "请使用备份管理标签页来恢复备份")

        except Exception as e:
            self.logger.error(f"恢复备份失败: {e}")
            QMessageBox.critical(self, "错误", f"恢复备份失败:\n{e}")
    
    # 信号处理方法
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)
        self.log_widget.append(f"状态: {message}")
    
    def on_operation_completed(self, operation: str, success: bool):
        """操作完成处理"""
        status = "成功" if success else "失败"
        self.log_widget.append(f"操作 {operation} {status}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("主窗口关闭")
        event.accept()
