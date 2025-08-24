#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帮助系统
提供在线帮助、操作演示和用户手册功能
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget,
    QWidget, QTreeWidget, QTreeWidgetItem, QSplitter,
    QScrollArea, QGroupBox, QFrame, QDialogButtonBox,
    QListWidget, QListWidgetItem, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextDocument

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.config_manager import ConfigManager


class HelpContentLoader(QThread):
    """帮助内容加载器"""
    
    content_loaded = pyqtSignal(str, str)  # topic, content
    loading_progress = pyqtSignal(int, str)
    
    def __init__(self, topic: str):
        super().__init__()
        self.topic = topic
        self.logger = get_logger("help_content_loader")
    
    def run(self):
        """加载帮助内容"""
        try:
            self.loading_progress.emit(20, "正在加载帮助内容...")
            self.msleep(200)
            
            content = self.load_help_content(self.topic)
            
            self.loading_progress.emit(100, "加载完成")
            self.content_loaded.emit(self.topic, content)
            
        except Exception as e:
            self.logger.error(f"加载帮助内容失败: {e}")
            self.content_loaded.emit(self.topic, f"加载失败: {e}")
    
    def load_help_content(self, topic: str) -> str:
        """加载指定主题的帮助内容"""
        help_contents = {
            "快速入门": """
# 快速入门指南

## 欢迎使用设备指纹识别与修改工具

本工具是一个专业的教学和研究平台，旨在帮助用户理解设备指纹识别技术的原理和实现方式。

### 主要功能

1. **系统状态监控**
   - 实时显示系统信息和性能数据
   - 监控权限状态和安全设置
   - 提供系统健康状况评估

2. **设备指纹管理**
   - 查看和管理网络适配器信息
   - 修改MAC地址（需要管理员权限）
   - 管理机器GUID和硬件标识

3. **备份管理**
   - 创建系统配置备份
   - 管理备份历史记录
   - 快速恢复系统设置

4. **教育功能**
   - 详细的技术原理解释
   - 分步骤的操作指导
   - 丰富的学习资源和参考资料

### 首次使用

1. **检查权限**：确保以管理员身份运行程序
2. **创建备份**：在进行任何修改前先创建系统备份
3. **了解风险**：仔细阅读每个功能的风险说明
4. **学习原理**：通过教育功能了解相关技术原理

### 安全提醒

⚠️ **重要提醒**：
- 本工具仅用于教学和研究目的
- 请在授权的环境中使用
- 遵守相关法律法规和网络使用政策
- 不得用于非法网络活动

### 获取帮助

如果您在使用过程中遇到问题，可以：
- 查看本帮助系统的详细说明
- 参考教育功能中的操作指导
- 查看日志信息了解错误详情
            """,
            
            "MAC地址修改": """
# MAC地址修改指南

## 什么是MAC地址

MAC地址（Media Access Control Address）是网络设备的物理地址，用于在网络中唯一标识设备。

### MAC地址格式
- 标准格式：XX:XX:XX:XX:XX:XX
- 其他格式：XX-XX-XX-XX-XX-XX、XXXXXXXXXXXX

### 修改步骤

1. **准备工作**
   - 确保具有管理员权限
   - 创建系统备份
   - 记录原始MAC地址

2. **选择适配器**
   - 在"设备指纹"标签页中查看网络适配器
   - 选择要修改的适配器
   - 点击"修改"按钮

3. **输入新MAC地址**
   - 输入有效的MAC地址格式
   - 可以使用"生成随机MAC"功能
   - 系统会自动验证格式

4. **确认修改**
   - 仔细阅读风险警告
   - 完成三级确认流程
   - 等待修改完成

### 注意事项

⚠️ **重要提醒**：
- 某些网卡不支持MAC地址修改
- 修改后可能需要重新连接网络
- 企业网络可能有MAC地址白名单
- 修改失败时请恢复原始MAC地址

### 故障排除

如果修改失败：
1. 检查网卡驱动是否支持MAC修改
2. 确认具有足够的系统权限
3. 尝试重启网络适配器
4. 必要时恢复原始MAC地址
            """,
            
            "机器GUID修改": """
# 机器GUID修改指南

## ⚠️ 高风险操作警告

机器GUID修改是一个高风险操作，可能导致严重后果。请仔细阅读本指南。

## 什么是机器GUID

机器GUID是Windows系统的唯一标识符，用于：
- 软件许可证验证
- 系统识别和跟踪
- 应用程序的设备绑定

### GUID格式
标准格式：XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

### 修改步骤

1. **风险评估**
   - 了解所有可能的风险和后果
   - 确保有完整的系统备份
   - 准备应急恢复方案

2. **创建备份**
   - 创建完整的系统备份
   - 备份注册表相关键值
   - 记录原始GUID值

3. **执行修改**
   - 在"设备指纹"标签页中找到机器GUID
   - 点击"修改GUID"按钮
   - 输入或生成新的GUID

4. **三级确认**
   - 完成严格的三级确认流程
   - 确认了解所有风险
   - 确认具备恢复能力

5. **重启系统**
   - 修改完成后必须重启系统
   - 检查系统功能是否正常
   - 验证相关软件是否正常运行

### 可能的风险

🚨 **严重风险**：
- 软件许可证可能失效
- Windows激活状态可能受影响
- 某些应用程序可能无法运行
- 系统稳定性可能受影响

### 恢复方案

如果出现问题：
1. 从备份恢复注册表
2. 恢复原始GUID值
3. 重新激活Windows
4. 重新安装受影响的软件
5. 使用系统还原功能

### 法律和伦理

⚠️ **重要提醒**：
- 仅在授权的系统上使用
- 不得用于绕过软件许可证限制
- 遵守相关法律法规
- 承担所有使用风险
            """,
            
            "备份与恢复": """
# 备份与恢复指南

## 备份的重要性

在进行任何系统修改前，创建备份是至关重要的安全措施。

### 备份类型

1. **完整备份**
   - 备份所有相关系统设置
   - 包括注册表、网络配置等
   - 恢复时间较长但最安全

2. **增量备份**
   - 只备份自上次备份后的变化
   - 备份速度快，占用空间小
   - 需要完整备份作为基础

3. **差异备份**
   - 备份自上次完整备份后的所有变化
   - 恢复速度比增量备份快
   - 占用空间适中

### 创建备份

1. **选择备份类型**
   - 在"备份管理"标签页中选择备份类型
   - 推荐首次使用完整备份

2. **配置备份选项**
   - 选择备份存储位置
   - 设置压缩和加密选项
   - 配置备份文件命名规则

3. **执行备份**
   - 点击"创建备份"按钮
   - 等待备份过程完成
   - 验证备份文件完整性

### 恢复系统

1. **选择恢复点**
   - 在备份历史中选择合适的备份
   - 查看备份详细信息
   - 确认备份文件完整性

2. **执行恢复**
   - 点击"恢复"按钮
   - 确认恢复操作
   - 等待恢复过程完成

3. **验证恢复结果**
   - 检查系统功能是否正常
   - 验证网络连接
   - 测试相关应用程序

### 最佳实践

✅ **建议**：
- 定期创建备份（建议每周一次）
- 保留多个备份版本
- 将备份存储在安全位置
- 定期测试备份的可用性
- 记录备份和恢复操作

### 故障排除

如果备份或恢复失败：
1. 检查磁盘空间是否充足
2. 确认具有足够的系统权限
3. 检查备份文件是否损坏
4. 尝试使用系统还原功能
5. 联系技术支持获取帮助
            """,
            
            "常见问题": """
# 常见问题解答

## 一般问题

### Q: 程序需要管理员权限吗？
A: 是的，大部分功能需要管理员权限才能正常工作。请以管理员身份运行程序。

### Q: 程序支持哪些操作系统？
A: 目前支持Windows 10和Windows 11。macOS支持正在开发中。

### Q: 如何确保操作安全？
A: 
- 在操作前创建完整的系统备份
- 仔细阅读风险警告
- 在测试环境中先进行验证
- 确保了解恢复方案

## MAC地址相关

### Q: 为什么MAC地址修改失败？
A: 可能的原因：
- 网卡不支持MAC地址修改
- 权限不足
- 网卡驱动问题
- MAC地址格式不正确

### Q: 修改MAC地址后网络无法连接？
A: 解决方案：
- 重启网络适配器
- 检查网络配置
- 恢复原始MAC地址
- 重新配置网络连接

### Q: 如何生成有效的MAC地址？
A: 
- 使用程序内置的随机生成功能
- 确保第一个字节的最低位为0（单播地址）
- 设置本地管理位（第一个字节的第二位为1）

## GUID相关

### Q: 修改GUID后软件无法激活？
A: 这是正常现象，因为：
- 软件许可证与机器GUID绑定
- 需要重新激活或重新安装软件
- 建议从备份恢复原始GUID

### Q: 如何恢复原始GUID？
A: 
- 从注册表备份恢复
- 使用系统还原功能
- 手动修改注册表键值
- 重新安装操作系统（最后手段）

## 备份相关

### Q: 备份文件存储在哪里？
A: 默认存储在程序目录的backups文件夹中，可以在设置中修改。

### Q: 备份文件可以在其他电脑上使用吗？
A: 不建议，因为：
- 硬件配置不同
- 系统环境差异
- 可能导致系统不稳定

### Q: 如何验证备份文件的完整性？
A: 
- 查看备份文件大小
- 检查备份日志
- 尝试部分恢复测试
- 使用文件校验工具

## 技术支持

### Q: 遇到问题如何获取帮助？
A: 
- 查看程序日志文件
- 参考本帮助系统
- 查看教育功能中的指导
- 在测试环境中重现问题

### Q: 如何报告程序错误？
A: 
- 记录详细的错误信息
- 保存相关日志文件
- 描述操作步骤
- 提供系统环境信息

### Q: 程序更新频率如何？
A:
- 定期发布功能更新
- 及时修复发现的问题
- 根据用户反馈改进功能
- 保持与最新系统的兼容性
            """,

            "学习资源": """
# 学习资源

## 技术文档

### 设备指纹识别技术
- **MAC地址原理**：了解MAC地址的结构和作用机制
- **GUID系统**：Windows机器GUID的生成和管理原理
- **网络协议**：以太网协议和网络标识符的工作原理
- **注册表结构**：Windows注册表中网络配置的存储方式

### 网络安全基础
- **网络身份识别**：设备在网络中的身份识别机制
- **MAC地址欺骗**：MAC地址修改的技术原理和应用场景
- **网络追踪技术**：基于设备指纹的网络追踪方法
- **隐私保护**：设备指纹与用户隐私保护的关系

## 实践指导

### 实验环境搭建
1. **虚拟机环境**
   - 使用VMware或VirtualBox创建测试环境
   - 配置网络适配器和虚拟网络
   - 创建系统快照便于恢复

2. **网络环境配置**
   - 搭建隔离的测试网络
   - 配置DHCP服务器
   - 设置网络监控工具

3. **安全措施**
   - 确保在授权环境中进行测试
   - 建立完整的备份和恢复机制
   - 制定应急响应预案

### 操作演练
1. **基础操作**
   - 查看和分析网络适配器信息
   - 理解MAC地址的组成和含义
   - 学习注册表的相关键值

2. **进阶操作**
   - 安全地修改MAC地址
   - 理解修改对网络连接的影响
   - 掌握恢复原始设置的方法

3. **高级应用**
   - 批量管理多个网络适配器
   - 自动化备份和恢复流程
   - 集成到系统管理脚本中

## 参考资料

### 技术标准
- **IEEE 802标准**：以太网和无线网络的技术标准
- **RFC文档**：网络协议的官方规范文档
- **Microsoft文档**：Windows系统网络配置的官方文档

### 学习网站
- **网络安全教育平台**：专业的网络安全学习资源
- **技术博客和论坛**：实践经验分享和问题讨论
- **开源项目**：相关工具的源代码和文档

### 书籍推荐
- 《网络安全技术与实践》
- 《Windows系统内核原理》
- 《网络协议分析与应用》
- 《信息安全管理与实践》

## 法律和伦理

### 使用规范
⚠️ **重要提醒**：
- 仅在授权的系统和网络环境中使用
- 不得用于非法网络活动或攻击行为
- 遵守当地法律法规和网络使用政策
- 尊重他人的网络权益和隐私

### 教育目的
- 本工具专为教学和研究设计
- 帮助理解网络安全技术原理
- 提高网络安全意识和防护能力
- 培养负责任的网络安全专业人员

### 责任声明
- 用户需承担所有使用风险和责任
- 开发团队不承担任何滥用后果
- 建议在专业指导下进行学习和实践
- 如有疑问请咨询相关法律专家

## 技术支持

### 获取帮助
- 查看程序内置的帮助文档
- 参考教育功能中的详细指导
- 查看日志文件了解详细信息
- 在测试环境中验证操作步骤

### 问题反馈
- 详细描述遇到的问题
- 提供相关的日志信息
- 说明操作系统和环境信息
- 描述重现问题的具体步骤

### 持续学习
- 关注网络安全技术的最新发展
- 参与相关的学术研究和讨论
- 实践中不断提高技术水平
- 分享经验帮助其他学习者
            """
        }

        return help_contents.get(topic, "帮助内容正在准备中...")


class QuickHelpWidget(QWidget):
    """快速帮助控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 快速链接
        quick_links_group = QGroupBox("快速链接")
        links_layout = QGridLayout(quick_links_group)
        
        # 创建快速链接按钮
        quick_links = [
            ("🚀 快速入门", "快速入门"),
            ("🔧 MAC地址修改", "MAC地址修改"),
            ("🆔 机器GUID修改", "机器GUID修改"),
            ("💾 备份与恢复", "备份与恢复"),
            ("❓ 常见问题", "常见问题"),
            ("📚 学习资源", "学习资源")
        ]
        
        for i, (text, topic) in enumerate(quick_links):
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=topic: self.open_help_topic(t))
            btn.setMinimumHeight(40)
            links_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(quick_links_group)
        
        # 最近查看
        recent_group = QGroupBox("最近查看")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(100)
        self.recent_list.itemDoubleClicked.connect(self.open_recent_topic)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        # 搜索功能
        search_group = QGroupBox("搜索帮助")
        search_layout = QVBoxLayout(search_group)
        
        search_info = QLabel("使用教育功能中的学习资源进行详细搜索")
        search_info.setStyleSheet("color: #666; font-style: italic;")
        search_layout.addWidget(search_info)
        
        layout.addWidget(search_group)
        
        layout.addStretch()
    
    def open_help_topic(self, topic: str):
        """打开帮助主题"""
        # 添加到最近查看
        self.add_to_recent(topic)

        # 查找帮助系统对话框并显示主题
        parent = self.parent()
        while parent and not isinstance(parent, HelpSystemDialog):
            parent = parent.parent()

        if parent and isinstance(parent, HelpSystemDialog):
            parent.show_help_topic(topic)
        else:
            # 如果找不到父对话框，尝试直接访问内容控件
            try:
                # 查找同级的内容控件
                dialog = self.window()
                if hasattr(dialog, 'content_widget'):
                    dialog.content_widget.show_help_topic(topic)
            except Exception as e:
                print(f"无法显示帮助主题 {topic}: {e}")
    
    def open_recent_topic(self, item: QListWidgetItem):
        """打开最近查看的主题"""
        topic = item.text()
        self.open_help_topic(topic)
    
    def add_to_recent(self, topic: str):
        """添加到最近查看"""
        # 检查是否已存在
        for i in range(self.recent_list.count()):
            if self.recent_list.item(i).text() == topic:
                self.recent_list.takeItem(i)
                break
        
        # 添加到顶部
        self.recent_list.insertItem(0, topic)
        
        # 限制最大数量
        while self.recent_list.count() > 5:
            self.recent_list.takeItem(self.recent_list.count() - 1)


class HelpContentWidget(QWidget):
    """帮助内容显示控件"""
    
    def __init__(self):
        super().__init__()
        self.current_topic = None
        self.content_loader = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel("选择帮助主题")
        self.title_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 打印按钮
        print_btn = QPushButton("打印")
        print_btn.clicked.connect(self.print_content)
        title_layout.addWidget(print_btn)
        
        layout.addLayout(title_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 内容显示
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setFont(QFont("Microsoft YaHei UI", 10))
        layout.addWidget(self.content_text)
        
        # 显示欢迎信息
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """
# 欢迎使用帮助系统

## 如何使用帮助系统

1. **快速链接**：点击左侧的快速链接按钮快速访问常用帮助主题
2. **最近查看**：查看最近访问过的帮助主题
3. **详细内容**：每个主题都提供详细的说明和操作指导

## 获取更多帮助

- 查看"教育功能"标签页中的详细学习资源
- 参考操作指导了解具体步骤
- 查看程序日志了解详细信息

## 安全提醒

⚠️ 请始终记住：
- 本工具仅用于教学和研究目的
- 在进行任何修改前请创建备份
- 仔细阅读风险警告和操作说明
- 遵守相关法律法规

选择左侧的帮助主题开始学习！
        """
        
        self.content_text.setMarkdown(welcome_text)
    
    def show_help_topic(self, topic: str):
        """显示帮助主题"""
        if self.content_loader and self.content_loader.isRunning():
            self.content_loader.terminate()
            self.content_loader.wait()
        
        self.current_topic = topic
        self.title_label.setText(f"帮助主题: {topic}")
        
        # 显示加载进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动内容加载器
        self.content_loader = HelpContentLoader(topic)
        self.content_loader.content_loaded.connect(self.on_content_loaded)
        self.content_loader.loading_progress.connect(self.on_loading_progress)
        self.content_loader.start()
    
    def on_content_loaded(self, topic: str, content: str):
        """内容加载完成"""
        if topic == self.current_topic:
            self.content_text.setMarkdown(content)
        
        self.progress_bar.setVisible(False)
        
        if self.content_loader:
            self.content_loader.deleteLater()
            self.content_loader = None
    
    def on_loading_progress(self, value: int, message: str):
        """加载进度更新"""
        self.progress_bar.setValue(value)
    
    def print_content(self):
        """打印内容"""
        if self.current_topic:
            try:
                # 尝试导入打印支持
                from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

                printer = QPrinter()
                dialog = QPrintDialog(printer, self)

                if dialog.exec_() == QPrintDialog.Accepted:
                    self.content_text.print_(printer)
            except ImportError:
                # 如果没有打印支持，显示提示信息
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "打印功能",
                                      "打印功能需要PyQt5打印支持模块。\n"
                                      "您可以复制内容到其他应用程序进行打印。")
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "打印错误", f"打印失败: {e}")


class HelpSystemDialog(QDialog):
    """帮助系统对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("help_system")
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("帮助系统")
        self.setFixedSize(900, 700)
        self.setModal(False)  # 允许与主窗口同时操作
        
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：快速帮助
        self.quick_help_widget = QuickHelpWidget()
        self.quick_help_widget.setMaximumWidth(250)
        splitter.addWidget(self.quick_help_widget)
        
        # 右侧：帮助内容
        self.content_widget = HelpContentWidget()
        splitter.addWidget(self.content_widget)
        
        # 设置分割器比例
        splitter.setSizes([250, 650])
        
        # 按钮区域
        button_box = QDialogButtonBox()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_box.addButton(close_btn, QDialogButtonBox.RejectRole)
        
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
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f8f8f8;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
        """)
    
    def show_help_topic(self, topic: str):
        """显示帮助主题"""
        self.content_widget.show_help_topic(topic)
    
    def closeEvent(self, event):
        """关闭事件"""
        self.logger.info("帮助系统关闭")
        event.accept()
