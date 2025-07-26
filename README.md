# CAJanus - 设备指纹识别与修改工具

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15.11+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/license-Educational-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/your-repo/CAJanus)
[![Version](https://img.shields.io/badge/version-v1.1.0-brightgreen.svg)](CHANGELOG.md)

> 🎓 **专为教学和研究设计的跨平台设备指纹识别与修改工具**

CAJanus是一款专业的设备指纹识别与修改工具，专门为网络安全教学和研究而设计。它提供了直观的图形界面，支持跨平台操作，并具备企业级的安全保护机制。

## 🆕 最新更新 (v1.1.0)

**重大功能修复与优化** - 2025年7月26日

- 🔧 **核心功能修复**: 修复了设备指纹识别、网络适配器属性访问等关键问题
- 📋 **菜单功能完善**: 实现了文件、工具、帮助菜单的所有功能
- ⚙️ **设置系统优化**: 完善了29个配置项，修复了配置键值映射问题
- 💾 **备份系统改进**: 标准化时间处理，新增删除、快速恢复、导出功能
- 🔧 **设备指纹完善**: 修复网络适配器、GUID恢复、卷序列号修改等功能
- 🎓 **教育功能优化**: 统一UI布局，优化内容组织和用户体验
- 🛠️ **技术架构优化**: 改进错误处理、跨平台兼容性和资源管理

> 📖 查看完整更新内容：[更新日志](CHANGELOG.md) | [技术修复详情](docs/technical/bug-fixes-v1.1.0.md)

## ✨ 主要特性

### 🔍 设备指纹识别
- **网络适配器检测**：获取MAC地址、IP地址、连接状态
- **硬件信息收集**：CPU、内存、磁盘、机器GUID等
- **系统信息监控**：操作系统、版本、架构、运行时间
- **跨平台支持**：Windows、macOS、Linux统一接口

### 🛡️ 安全修改功能
- **MAC地址修改**：安全修改网络适配器MAC地址
- **机器GUID修改**：修改Windows机器唯一标识符
- **三级确认系统**：严格的操作确认和风险管理
- **自动备份保护**：修改前自动创建系统备份

### 💾 备份与恢复
- **完整备份**：系统配置、网络设置、硬件信息
- **智能恢复**：验证备份完整性，安全恢复数据
- **历史管理**：备份文件管理和清理策略
- **增量备份**：支持增量和差异备份模式

### 🎨 现代化界面
- **响应式设计**：自适应不同屏幕尺寸和DPI缩放
- **多语言支持**：中文、英文、繁体中文、日语
- **无障碍功能**：键盘导航、高对比度、屏幕阅读器支持
- **主题系统**：多种界面主题可选

### 📚 教育功能
- **技术原理说明**：详细的设备指纹技术原理
- **操作指导**：分步骤的操作说明和注意事项
- **学习资源**：相关文档和参考资料链接
- **安全提醒**：法律合规和安全使用提醒

## 🚀 快速开始

### 系统要求

- **操作系统**：Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python版本**：3.8 或更高版本
- **内存**：至少 4GB RAM
- **存储空间**：至少 1GB 可用空间

### 安装方法

#### 方式一：源码安装

```bash
# 克隆仓库
git clone https://github.com/your-repo/CAJanus.git
cd CAJanus

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python gui_main.py
```

#### 方式二：二进制安装

从 [Releases](https://github.com/your-repo/CAJanus/releases) 页面下载对应平台的安装包：

- **Windows**：`CAJanus-1.0.0-windows.exe`
- **macOS**：`CAJanus-1.0.0.dmg`
- **Linux**：`CAJanus-1.0.0-x86_64.AppImage`

### 首次运行

1. **权限检查**：程序会自动检查所需的系统权限
2. **配置初始化**：首次运行会创建默认配置文件
3. **功能测试**：建议运行内置测试确保功能正常

## 📖 使用指南

### 基本操作流程

1. **查看系统状态**
   - 切换到"系统状态"标签页
   - 查看操作系统信息和权限状态
   - 监控系统性能指标

2. **检查设备指纹**
   - 切换到"设备指纹"标签页
   - 查看网络适配器和硬件信息
   - 记录当前的设备标识符

3. **创建备份**
   - 切换到"备份管理"标签页
   - 选择备份类型和存储位置
   - 执行备份操作

4. **安全修改**
   - 在相应功能页面选择要修改的项目
   - 通过三级确认系统确认操作
   - 系统自动执行修改和验证

### 高级功能

- **响应式界面**：支持多种屏幕尺寸自动适配
- **多语言切换**：在设置中选择界面语言
- **无障碍模式**：启用键盘导航和高对比度模式
- **帮助系统**：按F1或点击帮助菜单获取详细说明

## 🧪 开发与测试

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/ -v

# 代码质量检查
pylint src/
black src/
flake8 src/

# 生成文档
sphinx-build -b html docs/ docs/_build/
```

### 测试覆盖

- **单元测试**：核心模块功能测试
- **集成测试**：模块间协作测试
- **性能测试**：启动时间、内存使用、响应速度
- **用户体验测试**：界面响应性、易用性测试

### 构建打包

```bash
# 使用PyInstaller打包
pyinstaller build.spec

# 生成的可执行文件在dist/目录下
```

## 📚 文档

### 📖 用户文档
- [安装指南](docs/user-guide/installation.md) - 详细的安装步骤和环境配置
- [快速入门](docs/user-guide/quick-start.md) - 5分钟上手指南
- [用户手册](docs/user-guide/user-manual.md) - 完整的功能使用说明
- [常见问题](docs/user-guide/faq.md) - 常见问题解答
- [故障排除](docs/user-guide/troubleshooting.md) - 问题诊断和解决方案

### 🔧 开发文档
- [开发指南](docs/developer-guide/development-guide.md) - 开发环境搭建和流程
- [架构设计](docs/developer-guide/architecture.md) - 系统架构和设计原理
- [API参考](docs/developer-guide/api-reference.md) - 接口文档和使用示例

### 🚀 运维文档
- [部署指南](docs/deployment/deployment-guide.md) - 生产环境部署方案
- [配置管理](docs/deployment/configuration.md) - 配置文件和参数说明

### 📋 项目文档
- [项目总结](docs/project/project-summary.md) - 项目成果和价值评估
- [发展路线图](docs/project/roadmap.md) - 未来发展规划
- [文档中心](docs/README.md) - 完整的文档导航

## 🤝 贡献指南

我们欢迎社区贡献！请阅读 [贡献指南](CONTRIBUTING.md) 了解如何参与项目开发。

### 贡献方式

- 🐛 **报告Bug**：在Issues中报告发现的问题
- 💡 **功能建议**：提出新功能或改进建议
- 📝 **文档改进**：完善文档和示例
- 🔧 **代码贡献**：提交Pull Request

### 开发流程

1. Fork项目到你的GitHub账户
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

## 📄 许可证

本项目仅供教育和研究使用，严禁用于任何非法目的。详见 [LICENSE](LICENSE) 文件。

### 使用条款

- ✅ **教育目的**：学习设备指纹技术原理
- ✅ **研究用途**：网络安全相关研究
- ✅ **授权环境**：仅在自己拥有或获得授权的设备上使用
- ❌ **商业用途**：禁止用于任何商业目的
- ❌ **恶意使用**：禁止用于任何非法或恶意活动

## 🆘 支持与帮助

### 获取帮助

- 📖 **文档**：查看详细的用户手册和技术文档
- 💬 **讨论**：在GitHub Discussions中参与讨论
- 🐛 **问题报告**：在GitHub Issues中报告问题
- 📧 **邮件支持**：support@example.com

### 常见问题

**Q: 程序需要管理员权限吗？**
A: 某些功能（如修改MAC地址）需要管理员权限，程序会自动检查并提示。

**Q: 支持哪些操作系统？**
A: 支持Windows 10+、macOS 10.14+、Ubuntu 18.04+及其他主流Linux发行版。

**Q: 如何恢复修改前的设置？**
A: 程序会在修改前自动创建备份，可以通过"备份管理"功能恢复。

## 🏆 致谢

感谢以下开源项目和社区的支持：

- [PyQt5](https://pypi.org/project/PyQt5/) - 优秀的Python GUI框架
- [psutil](https://pypi.org/project/psutil/) - 跨平台系统监控库
- [PyYAML](https://pypi.org/project/PyYAML/) - YAML配置文件处理
- 所有贡献者和用户的支持与反馈

## 📊 项目状态

- **开发状态**：✅ 已完成，生产就绪
- **版本**：v1.0.0
- **最后更新**：2024年1月15日
- **维护状态**：🔄 积极维护中

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**

[🌟 Star](https://github.com/your-repo/CAJanus/stargazers) | 
[🍴 Fork](https://github.com/your-repo/CAJanus/fork) | 
[📥 Download](https://github.com/your-repo/CAJanus/releases)

</div>
