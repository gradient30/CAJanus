#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教育功能界面
提供原理解释、操作指导和学习资源
"""

import sys
from pathlib import Path
from typing import Dict, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget,
    QGroupBox, QScrollArea, QTreeWidget, QTreeWidgetItem,
    QSplitter, QFrame, QComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.config_manager import ConfigManager


class PrincipleExplanationWidget(QWidget):
    """原理解释控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_principles()
    
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：主题列表
        topics_group = QGroupBox("学习主题")
        topics_layout = QVBoxLayout(topics_group)
        
        self.topics_tree = QTreeWidget()
        self.topics_tree.setHeaderLabel("主题")
        self.topics_tree.itemClicked.connect(self.on_topic_selected)
        topics_layout.addWidget(self.topics_tree)
        
        splitter.addWidget(topics_group)
        
        # 右侧：内容显示
        content_group = QGroupBox("内容详情")
        content_layout = QVBoxLayout(content_group)
        
        # 标题
        self.content_title = QLabel("请选择一个学习主题")
        self.content_title.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.content_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.content_title)
        
        # 内容文本
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setFont(QFont("Microsoft YaHei UI", 10))
        self.content_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
                selection-background-color: #3d3d3d;
            }
        """)
        content_layout.addWidget(self.content_text)
        
        splitter.addWidget(content_group)
        
        # 设置分割器比例
        splitter.setSizes([300, 700])
    
    def load_principles(self):
        """加载原理内容"""
        principles = {
            "设备指纹基础": {
                "什么是设备指纹": """
设备指纹（Device Fingerprinting）是一种通过收集设备的各种特征信息来唯一标识设备的技术。

主要特征包括：
• 硬件特征：CPU型号、内存大小、硬盘信息等
• 网络特征：MAC地址、IP地址、网络配置等
• 系统特征：操作系统版本、安装的软件等
• 行为特征：使用习惯、访问模式等

设备指纹技术广泛应用于：
• 用户身份验证
• 反欺诈检测
• 广告投放
• 安全监控
                """,
                "设备指纹的工作原理": """
设备指纹的工作原理基于以下几个步骤：

1. 信息收集
   - 通过各种API和系统调用收集设备信息
   - 包括硬件、软件、网络等多维度信息

2. 特征提取
   - 从收集的信息中提取关键特征
   - 去除易变的信息，保留稳定特征

3. 指纹生成
   - 将特征信息组合成唯一标识
   - 通常使用哈希算法生成指纹

4. 指纹匹配
   - 将新生成的指纹与已知指纹比较
   - 判断是否为同一设备
                """,
                "常见的指纹技术": """
常见的设备指纹技术包括：

1. 浏览器指纹
   - User-Agent字符串
   - 屏幕分辨率和颜色深度
   - 时区和语言设置
   - 插件和字体列表

2. 硬件指纹
   - CPU信息和性能特征
   - GPU信息和渲染能力
   - 音频设备特征
   - 传感器数据

3. 网络指纹
   - IP地址和地理位置
   - 网络延迟特征
   - MTU大小
   - TCP/IP栈特征

4. 行为指纹
   - 鼠标移动模式
   - 键盘输入节奏
   - 触摸屏操作习惯
                """
            },
            "MAC地址管理": {
                "MAC地址基础": """
MAC地址（Media Access Control Address）是网络设备的物理地址。

特点：
• 长度：48位（6字节）
• 格式：XX:XX:XX:XX:XX:XX
• 唯一性：理论上全球唯一
• 分配：由IEEE统一分配给厂商

MAC地址结构：
• 前24位：厂商标识符（OUI）
• 后24位：设备标识符

常见用途：
• 网络通信中的设备识别
• 网络访问控制
• 设备跟踪和管理
                """,
                "MAC地址修改原理": """
MAC地址修改的技术原理：

1. 软件层面修改
   - 修改网络驱动程序中的MAC地址
   - 通过系统API更改网卡配置
   - 重启网络服务使修改生效

2. 修改方法（Windows）
   - 注册表修改
   - 设备管理器修改
   - 命令行工具修改

3. 修改方法（macOS/Linux）
   - ifconfig命令
   - ip命令
   - 网络配置文件修改

注意事项：
• 修改可能影响网络连接
• 某些网卡不支持MAC地址修改
• 修改后需要重启网络接口
                """,
                "MAC地址安全考虑": """
MAC地址相关的安全考虑：

1. 隐私保护
   - MAC地址可用于设备跟踪
   - 公共WiFi环境下的隐私风险
   - 随机化MAC地址的重要性

2. 网络安全
   - MAC地址欺骗攻击
   - ARP欺骗和中间人攻击
   - 网络访问控制绕过

3. 防护措施
   - 定期更换MAC地址
   - 使用VPN保护网络流量
   - 关闭不必要的网络发现功能

4. 法律和伦理
   - 遵守相关法律法规
   - 仅在授权环境下进行测试
   - 尊重他人隐私权
                """
            },
            "系统安全": {
                "权限管理": """
操作系统权限管理基础：

1. Windows权限模型
   - 用户账户控制（UAC）
   - 管理员权限和标准用户权限
   - 访问控制列表（ACL）

2. macOS权限模型
   - 系统完整性保护（SIP）
   - 管理员权限和标准用户权限
   - 权限请求机制

3. 权限提升
   - 合法的权限提升方法
   - 权限提升的安全风险
   - 最小权限原则

4. 安全最佳实践
   - 定期审查权限设置
   - 使用强密码和多因素认证
   - 及时更新系统和软件
                """,
                "注册表安全": """
Windows注册表安全管理：

1. 注册表基础
   - 注册表的结构和作用
   - 主要的注册表键值
   - 注册表的备份和恢复

2. 安全风险
   - 恶意软件修改注册表
   - 错误修改导致系统故障
   - 隐私信息泄露

3. 保护措施
   - 定期备份注册表
   - 使用注册表监控工具
   - 限制注册表访问权限

4. 最佳实践
   - 谨慎修改系统关键键值
   - 使用专业工具进行修改
   - 建立修改记录和回滚计划
                """
            }
        }
        
        # 构建树形结构
        for category, topics in principles.items():
            category_item = QTreeWidgetItem(self.topics_tree)
            category_item.setText(0, category)
            category_item.setData(0, Qt.UserRole, {"type": "category", "content": ""})
            
            for topic, content in topics.items():
                topic_item = QTreeWidgetItem(category_item)
                topic_item.setText(0, topic)
                topic_item.setData(0, Qt.UserRole, {"type": "topic", "content": content})
        
        # 展开所有项目
        self.topics_tree.expandAll()
    
    def on_topic_selected(self, item: QTreeWidgetItem, column: int):
        """主题选择事件"""
        data = item.data(0, Qt.UserRole)
        if data and data["type"] == "topic":
            self.content_title.setText(item.text(0))
            self.content_text.setPlainText(data["content"])


class OperationGuideWidget(QWidget):
    """操作指导控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_guides()
    
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout(self)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # 左侧：操作列表
        operations_group = QGroupBox("操作指导")
        operations_layout = QVBoxLayout(operations_group)

        self.operations_tree = QTreeWidget()
        self.operations_tree.setHeaderLabel("操作类型")
        self.operations_tree.itemClicked.connect(self.on_operation_selected)
        operations_layout.addWidget(self.operations_tree)

        splitter.addWidget(operations_group)

        # 右侧：指导内容
        content_group = QGroupBox("详细指导")
        content_layout = QVBoxLayout(content_group)

        # 内容标题
        self.content_title = QLabel("选择左侧操作查看详细指导")
        self.content_title.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.content_title.setStyleSheet("color: #2c3e50; padding: 10px;")
        content_layout.addWidget(self.content_title)

        # 内容文本
        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.guide_text.setFont(QFont("Microsoft YaHei UI", 10))
        self.guide_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
                selection-background-color: #3d3d3d;
            }
        """)
        content_layout.addWidget(self.guide_text)

        splitter.addWidget(content_group)

        # 设置分割器比例
        splitter.setSizes([300, 500])
    
    def load_guides(self):
        """加载操作指导"""
        self.guides = {
            "设备指纹管理": {
                "修改MAC地址": """# MAC地址修改操作指导

## 前期准备

### 步骤1：备份当前配置
• 记录当前MAC地址
• 创建系统备份点
• 确保有恢复方案

### 步骤2：检查权限
• 确认具有管理员权限
• 关闭相关安全软件
• 准备权限提升

## 执行操作

### 步骤3：执行修改
• 打开设备管理器
• 找到目标网络适配器
• 修改高级属性中的网络地址

### 步骤4：验证修改
• 重启网络适配器
• 检查新MAC地址
• 测试网络连接

## 问题处理

### 步骤5：故障排除
• 如果网络无法连接，恢复原MAC地址
• 检查网卡驱动是否支持MAC修改
• 必要时重启系统

## 注意事项
⚠️ 某些网卡不支持MAC地址修改
⚠️ 修改后可能需要重新连接网络
⚠️ 企业网络可能有MAC地址白名单
""",
                "修改机器GUID": """# 机器GUID修改操作指导

## 风险评估

### 步骤1：理解风险
• 机器GUID是系统重要标识
• 修改可能影响软件激活
• 某些程序可能无法正常运行

### 步骤2：创建备份
• 备份注册表相关键值
• 记录原始GUID值
• 创建系统还原点

## 执行操作

### 步骤3：修改注册表
• 打开注册表编辑器
• 导航到HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography
• 修改MachineGuid键值

### 步骤4：生成新GUID
• 使用GUID生成工具
• 确保格式正确
• 避免使用已知的GUID

## 验证测试

### 步骤5：验证和测试
• 重启系统
• 检查系统功能
• 测试相关软件

## 注意事项
⚠️ 修改GUID可能导致软件许可问题
⚠️ 某些系统服务可能受到影响
⚠️ 建议在虚拟机中先行测试
""",
                "恢复原始设置": """# 恢复原始设置操作指导

## 恢复准备

### 步骤1：确认恢复需求
• 确定需要恢复的设置项
• 检查备份文件的完整性
• 评估恢复的影响范围

### 步骤2：准备恢复环境
• 确保系统稳定运行
• 关闭不必要的程序
• 准备管理员权限

## 执行恢复

### 步骤3：选择恢复方式
• 使用系统备份恢复
• 手动恢复单项设置
• 使用工具自动恢复

### 步骤4：执行恢复操作
• 按照备份时间选择恢复点
• 确认恢复的设置项
• 执行恢复操作

## 验证结果

### 步骤5：验证恢复结果
• 检查恢复的设置是否正确
• 测试系统功能是否正常
• 确认网络连接状态

## 注意事项
⚠️ 恢复操作可能需要重启系统
⚠️ 部分设置恢复后需要重新配置
⚠️ 建议逐项验证恢复结果
"""
            },
            "系统备份管理": {
                "创建系统备份": """# 创建系统备份操作指导

## 备份准备

### 步骤1：评估备份需求
• 确定需要备份的内容
• 选择合适的备份类型
• 估算所需存储空间

### 步骤2：准备备份环境
• 检查磁盘空间
• 确保系统稳定
• 关闭不必要的程序

## 执行备份

### 步骤3：配置备份选项
• 选择备份路径
• 设置备份类型（完整/增量）
• 配置压缩和加密选项

### 步骤4：执行备份操作
• 启动备份进程
• 监控备份进度
• 处理可能的错误

## 验证备份

### 步骤5：验证备份完整性
• 检查备份文件大小
• 验证备份文件完整性
• 测试备份文件可读性

## 注意事项
⚠️ 备份过程中避免修改系统设置
⚠️ 确保备份存储位置安全可靠
⚠️ 定期验证备份文件的有效性
""",
                "恢复系统备份": """# 恢复系统备份操作指导

## 恢复准备

### 步骤1：选择恢复点
• 查看可用的备份文件
• 根据时间选择合适的恢复点
• 确认备份文件完整性

### 步骤2：准备恢复环境
• 确保系统处于安全状态
• 关闭所有应用程序
• 准备管理员权限

## 执行恢复

### 步骤3：配置恢复选项
• 选择恢复范围
• 设置恢复策略
• 确认恢复目标

### 步骤4：执行恢复操作
• 启动恢复进程
• 监控恢复进度
• 处理恢复过程中的问题

## 验证恢复

### 步骤5：验证恢复结果
• 检查恢复的设置
• 测试系统功能
• 确认所有服务正常

## 注意事项
⚠️ 恢复操作不可逆，请谨慎操作
⚠️ 恢复后可能需要重启系统
⚠️ 建议在恢复前创建当前状态备份
"""
            }
        }

        # 构建树形结构
        self.operations_tree.clear()
        for category, operations in self.guides.items():
            category_item = QTreeWidgetItem(self.operations_tree)
            category_item.setText(0, category)
            category_item.setData(0, Qt.UserRole, {"type": "category", "name": category})

            for operation, content in operations.items():
                operation_item = QTreeWidgetItem(category_item)
                operation_item.setText(0, operation)
                operation_item.setData(0, Qt.UserRole, {
                    "type": "operation",
                    "name": operation,
                    "content": content
                })

        # 展开所有项目
        self.operations_tree.expandAll()

    def on_operation_selected(self, item, column):
        """操作选择事件"""
        data = item.data(0, Qt.UserRole)
        if data and data["type"] == "operation":
            self.content_title.setText(data["name"])
            # 使用setPlainText而不是setMarkdown，因为PyQt5可能不支持
            self.guide_text.setPlainText(data["content"])



class LearningResourcesWidget(QWidget):
    """学习资源控件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_resources()
    
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout(self)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # 左侧：资源分类
        categories_group = QGroupBox("学习资源")
        categories_layout = QVBoxLayout(categories_group)

        self.resources_tree = QTreeWidget()
        self.resources_tree.setHeaderLabel("资源分类")
        self.resources_tree.itemClicked.connect(self.on_resource_selected)
        categories_layout.addWidget(self.resources_tree)

        splitter.addWidget(categories_group)

        # 右侧：资源内容
        content_group = QGroupBox("详细内容")
        content_layout = QVBoxLayout(content_group)

        # 内容标题
        self.content_title = QLabel("选择左侧资源查看详细内容")
        self.content_title.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.content_title.setStyleSheet("color: #2c3e50; padding: 10px;")
        content_layout.addWidget(self.content_title)

        # 内容文本
        self.resources_text = QTextEdit()
        self.resources_text.setReadOnly(True)
        self.resources_text.setFont(QFont("Microsoft YaHei UI", 10))
        self.resources_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
                selection-background-color: #3d3d3d;
            }
        """)
        content_layout.addWidget(self.resources_text)

        splitter.addWidget(content_group)

        # 设置分割器比例
        splitter.setSizes([300, 500])
    
    def load_resources(self):
        """加载学习资源"""
        self.resources = {
            "技术文档": {
                "IEEE 802标准文档": """# IEEE 802标准文档

## 文档概述
IEEE 802标准是局域网和城域网的重要技术标准，涵盖了网络协议和MAC地址相关的官方规范。

## 主要内容
- **MAC地址分配规则**: 如何分配和管理MAC地址
- **网络协议标准**: 以太网、无线网络等协议规范
- **设备识别机制**: 网络设备的唯一标识方法

## 学习价值
- 理解MAC地址的官方定义和标准
- 掌握网络设备识别的技术原理
- 了解网络协议的底层实现

## 访问方式
- 官方网站: https://standards.ieee.org/standard/802-2014.html
- 可通过IEEE官网免费查阅部分内容
- 完整文档需要购买或通过学术机构访问

## 相关标准
- IEEE 802.3: 以太网标准
- IEEE 802.11: 无线局域网标准
- IEEE 802.1: 网络架构和管理标准
""",
                "Windows注册表参考": """# Windows注册表参考

## 文档概述
Microsoft官方的Windows注册表完整参考文档，详细介绍了注册表的结构、功能和管理方法。

## 核心内容
- **注册表结构**: HKEY根键的组织和作用
- **数据类型**: REG_SZ、REG_DWORD等数据类型说明
- **安全机制**: 注册表权限和访问控制
- **备份恢复**: 注册表的备份和恢复方法

## 重要章节
### 系统标识相关
- MachineGuid: 机器唯一标识符
- InstallDate: 系统安装时间
- ProductId: 产品标识符

### 网络配置相关
- NetworkCards: 网络适配器配置
- Tcpip: TCP/IP协议配置
- Interfaces: 网络接口设置

## 学习建议
1. 先理解注册表的基本概念
2. 重点关注系统标识相关键值
3. 实践时务必先备份
4. 使用官方工具进行操作

## 访问地址
https://docs.microsoft.com/en-us/windows/win32/sysinfo/registry
""",
                "GUID技术规范": """# GUID技术规范

## 技术概述
GUID (Globally Unique Identifier) 是微软对UUID (Universally Unique Identifier) 的实现，用于在分布式系统中创建唯一标识符。

## 技术特点
- **全局唯一性**: 在时间和空间上保证唯一性
- **128位长度**: 提供足够大的标识空间
- **多种生成算法**: 支持不同的生成策略

## 生成算法
### 版本1 (时间戳+MAC地址)
- 基于时间戳和MAC地址生成
- 可以追溯生成时间和位置
- 存在隐私泄露风险

### 版本4 (随机数)
- 基于随机数或伪随机数生成
- 无法追溯生成信息
- 推荐用于隐私敏感场景

## 在Windows中的应用
- **机器GUID**: 标识计算机硬件
- **软件标识**: 应用程序和组件标识
- **用户标识**: 用户账户和会话标识

## 格式规范
标准格式: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
示例: 550e8400-e29b-41d4-a716-446655440000

## 技术参考
- RFC 4122: UUID标准规范
- Microsoft GUID文档
- .NET Framework GUID类参考
"""
            },
            "学习教程": {
                "网络安全基础教程": """# 网络安全基础教程

## 课程目标
掌握网络安全的基础概念，理解设备指纹识别技术的原理和应用。

## 第一章：网络基础知识
### 1.1 网络协议栈
- OSI七层模型
- TCP/IP协议族
- 数据链路层和网络层

### 1.2 网络设备标识
- MAC地址的作用和结构
- IP地址的分配和管理
- 设备指纹的概念

## 第二章：设备指纹技术
### 2.1 硬件指纹
- MAC地址指纹
- 硬件序列号
- CPU和主板标识

### 2.2 软件指纹
- 操作系统指纹
- 浏览器指纹
- 应用程序指纹

### 2.3 行为指纹
- 网络行为模式
- 时间模式分析
- 流量特征识别

## 第三章：隐私保护技术
### 3.1 指纹伪装技术
- MAC地址随机化
- User-Agent伪装
- 网络代理技术

### 3.2 匿名化技术
- Tor网络原理
- VPN技术应用
- 混淆网络流量

## 实践项目
1. 网络设备扫描实验
2. MAC地址修改实践
3. 设备指纹检测工具开发

## 学习资源
- 网络安全相关书籍推荐
- 在线课程和视频教程
- 开源工具和项目
""",
                "系统管理实践指南": """# 系统管理实践指南

## 指南概述
本指南涵盖Windows和macOS系统管理的核心技能，重点关注系统标识和网络配置管理。

## Windows系统管理

### 注册表管理
#### 基础操作
- 注册表编辑器的使用
- 注册表备份和恢复
- 权限管理和安全设置

#### 高级技巧
- 批量修改注册表项
- 注册表监控和审计
- 自动化脚本编写

### 网络配置管理
#### 网络适配器管理
- 适配器属性配置
- MAC地址管理
- 网络协议设置

#### 网络诊断工具
- ipconfig命令详解
- netsh工具使用
- 网络连接故障排除

## macOS系统管理

### 系统配置管理
#### 系统偏好设置
- 网络配置管理
- 安全和隐私设置
- 用户和群组管理

#### 命令行工具
- networksetup命令
- ifconfig命令使用
- 系统信息查询

### 网络管理
#### 网络接口管理
- 以太网配置
- Wi-Fi网络管理
- 网络服务配置

## 跨平台管理技巧

### 自动化脚本
- PowerShell脚本 (Windows)
- Shell脚本 (macOS/Linux)
- Python自动化工具

### 监控和日志
- 系统日志分析
- 网络流量监控
- 性能指标收集

## 最佳实践
1. 定期备份系统配置
2. 建立变更管理流程
3. 实施安全基线配置
4. 持续监控系统状态

## 故障排除指南
- 常见问题诊断方法
- 系统恢复策略
- 应急响应流程
""",
                "设备指纹检测技术": """# 设备指纹检测技术

## 技术概述
设备指纹检测是通过收集设备的各种特征信息，生成唯一标识符的技术。

## 检测维度

### 硬件特征
#### 网络硬件
- MAC地址: 网络适配器的物理地址
- 网卡厂商: 通过OUI识别制造商
- 网络接口数量: 有线、无线接口统计

#### 系统硬件
- CPU信息: 型号、核心数、频率
- 内存配置: 容量、类型、速度
- 存储设备: 硬盘型号、序列号

### 软件特征
#### 操作系统
- 系统版本: Windows、macOS、Linux版本
- 系统语言: 区域设置和语言包
- 安装时间: 系统首次安装时间

#### 应用软件
- 浏览器信息: 类型、版本、插件
- 安装软件: 软件列表和版本信息
- 系统服务: 运行的系统服务

### 配置特征
#### 网络配置
- IP地址: 内网和公网IP
- DNS设置: DNS服务器配置
- 代理设置: HTTP/HTTPS代理配置

#### 系统配置
- 时区设置: 系统时区和时间格式
- 显示设置: 分辨率、颜色深度
- 字体配置: 安装的字体列表

## 检测方法

### 主动检测
- WMI查询 (Windows)
- System Information (macOS)
- /proc文件系统 (Linux)

### 被动检测
- 网络流量分析
- 协议指纹识别
- 行为模式分析

## 应用场景
1. **设备管理**: 企业设备资产管理
2. **安全防护**: 异常设备检测
3. **用户追踪**: 用户行为分析
4. **反欺诈**: 设备风险评估

## 隐私考虑
- 数据收集的合法性
- 用户知情同意
- 数据存储和传输安全
- 匿名化处理技术

## 对抗技术
- 指纹伪装和混淆
- 虚拟化环境使用
- 代理和VPN技术
- 定期更换设备特征
"""
            },
            "工具软件": {
                "网络分析工具": """# 网络分析工具

## Wireshark
### 功能特点
- 强大的网络协议分析器
- 支持数百种网络协议
- 实时捕获和离线分析
- 跨平台支持

### 主要用途
- 网络故障诊断
- 协议分析和学习
- 安全审计和渗透测试
- 网络性能优化

### 学习建议
1. 从基础的HTTP/TCP分析开始
2. 学习过滤器语法
3. 掌握统计分析功能
4. 实践不同协议的分析

## Nmap
### 功能特点
- 网络发现和安全扫描
- 端口扫描和服务识别
- 操作系统指纹识别
- 脚本引擎支持

### 常用命令
- `nmap -sn 192.168.1.0/24`: 主机发现
- `nmap -sS target`: TCP SYN扫描
- `nmap -O target`: 操作系统检测
- `nmap --script vuln target`: 漏洞扫描

### 学习路径
1. 基础扫描技术
2. 高级扫描选项
3. 脚本引擎使用
4. 结果分析和报告
""",
                "系统管理工具": """# 系统管理工具

## PowerShell (Windows)
### 核心特性
- 面向对象的命令行界面
- 强大的脚本编程能力
- 与.NET Framework集成
- 远程管理支持

### 常用命令
- `Get-WmiObject`: WMI对象查询
- `Get-NetAdapter`: 网络适配器信息
- `Set-NetAdapter`: 网络适配器配置
- `Get-ComputerInfo`: 系统信息查询

### 实用脚本示例
```powershell
# 获取网络适配器MAC地址
Get-NetAdapter | Select-Object Name, MacAddress

# 修改网络适配器MAC地址
Set-NetAdapter -Name "以太网" -MacAddress "00:11:22:33:44:55"
```

## Terminal (macOS)
### 核心功能
- Unix命令行环境
- Shell脚本支持
- 系统管理和配置
- 开发工具集成

### 常用命令
- `ifconfig`: 网络接口配置
- `networksetup`: 网络设置管理
- `system_profiler`: 系统信息查询
- `sudo`: 权限提升

### 实用命令示例
```bash
# 查看网络接口信息
ifconfig en0

# 修改MAC地址
sudo ifconfig en0 ether 00:11:22:33:44:55
```

## 跨平台工具
### Python
- 丰富的网络库支持
- 跨平台兼容性
- 自动化脚本开发
- 数据分析和可视化
""",
                "开发调试工具": """# 开发调试工具

## 集成开发环境

### Visual Studio Code
- 轻量级代码编辑器
- 丰富的插件生态
- 内置终端和调试器
- Git集成支持

### PyCharm
- Python专业开发环境
- 智能代码补全
- 强大的调试功能
- 数据库工具集成

## 调试工具

### Process Monitor (Windows)
- 实时文件系统监控
- 注册表访问监控
- 进程和线程活动
- 网络活动监控

### Activity Monitor (macOS)
- 系统资源监控
- 进程管理和分析
- 网络活动监控
- 磁盘使用情况

## 网络调试

### Postman
- API测试和开发
- 请求构建和发送
- 响应分析和验证
- 自动化测试脚本

### Burp Suite
- Web应用安全测试
- HTTP代理和拦截
- 漏洞扫描和分析
- 扩展插件支持

## 版本控制

### Git
- 分布式版本控制
- 分支管理和合并
- 远程仓库同步
- 协作开发支持

### GitHub/GitLab
- 代码托管平台
- 项目管理工具
- CI/CD集成
- 社区协作功能
"""
            }
        }

        # 构建树形结构
        self.resources_tree.clear()
        for category, resources in self.resources.items():
            category_item = QTreeWidgetItem(self.resources_tree)
            category_item.setText(0, category)
            category_item.setData(0, Qt.UserRole, {"type": "category", "name": category})

            for resource, content in resources.items():
                resource_item = QTreeWidgetItem(category_item)
                resource_item.setText(0, resource)
                resource_item.setData(0, Qt.UserRole, {
                    "type": "resource",
                    "name": resource,
                    "content": content
                })

        # 展开所有项目
        self.resources_tree.expandAll()

    def on_resource_selected(self, item, column):
        """资源选择事件"""
        data = item.data(0, Qt.UserRole)
        if data and data["type"] == "resource":
            self.content_title.setText(data["name"])
            # 使用setPlainText而不是setMarkdown，因为PyQt5可能不支持
            self.resources_text.setPlainText(data["content"])



class EducationWidget(QWidget):
    """教育功能主控件"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("education_widget")
        self.config_manager = ConfigManager()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 原理解释标签页
        self.principle_widget = PrincipleExplanationWidget()
        self.tab_widget.addTab(self.principle_widget, "原理解释")
        
        # 操作指导标签页
        self.guide_widget = OperationGuideWidget()
        self.tab_widget.addTab(self.guide_widget, "操作指导")
        
        # 学习资源标签页
        self.resources_widget = LearningResourcesWidget()
        self.tab_widget.addTab(self.resources_widget, "学习资源")
        
        # 底部信息
        info_layout = QHBoxLayout()
        info_label = QLabel("💡 提示: 本工具仅用于教学和研究目的，请遵守相关法律法规")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
