# 安装指南

本指南将帮助您在不同操作系统上安装和配置CAJanus。

## 📋 系统要求

### 最低要求
- **操作系统**：Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python版本**：3.8 或更高版本
- **内存**：4GB RAM
- **存储空间**：1GB 可用空间
- **显示器**：1024x768 分辨率

### 推荐配置
- **操作系统**：Windows 11, macOS 13+, Ubuntu 22.04+
- **Python版本**：3.9 或更高版本
- **内存**：8GB RAM 或更多
- **存储空间**：2GB 可用空间
- **显示器**：1920x1080 分辨率或更高

## 🚀 快速安装

### 方式一：使用预编译包（推荐）

#### Windows
1. 下载 [CAJanus-1.0.0-windows-x64.exe](https://github.com/your-repo/CAJanus/releases)
2. 右键点击安装包，选择"以管理员身份运行"
3. 按照安装向导完成安装
4. 从开始菜单启动CAJanus

#### macOS
1. 下载 [CAJanus-1.0.0-darwin-x64.dmg](https://github.com/your-repo/CAJanus/releases)
2. 双击DMG文件挂载磁盘映像
3. 将CAJanus.app拖拽到Applications文件夹
4. 从启动台或应用程序文件夹启动

#### Linux
1. 下载 [CAJanus-1.0.0-linux-x64.AppImage](https://github.com/your-repo/CAJanus/releases)
2. 添加执行权限：`chmod +x CAJanus-1.0.0-linux-x64.AppImage`
3. 双击运行或命令行执行：`./CAJanus-1.0.0-linux-x64.AppImage`

### 方式二：从源码安装

#### 1. 获取源码
```bash
# 克隆仓库
git clone https://github.com/your-repo/CAJanus.git
cd CAJanus

# 或下载源码包
wget https://github.com/your-repo/CAJanus/archive/v1.0.0.tar.gz
tar -xzf v1.0.0.tar.gz
cd CAJanus-1.0.0
```

#### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 3. 安装依赖
```bash
# 升级pip
python -m pip install --upgrade pip

# 安装运行时依赖
pip install -r requirements.txt
```

#### 4. 验证安装
```bash
# 运行环境检查
python check_environment.py

# 启动应用程序
python gui_main.py
```

## 🔧 详细安装步骤

### Windows 详细安装

#### 前置条件
1. **Python安装**
   - 访问 [Python官网](https://www.python.org/downloads/) 下载Python 3.8+
   - 安装时勾选"Add Python to PATH"
   - 验证安装：`python --version`

2. **Git安装**（可选，用于源码安装）
   - 下载 [Git for Windows](https://git-scm.com/download/win)
   - 使用默认设置完成安装

#### 源码安装步骤
```cmd
# 1. 克隆项目
git clone https://github.com/your-repo/CAJanus.git
cd CAJanus

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行环境检查
python check_environment.py

# 5. 启动应用
python gui_main.py
```

### macOS 详细安装

#### 前置条件
1. **Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

2. **Homebrew**（推荐）
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Python安装**
   ```bash
   # 使用Homebrew安装
   brew install python@3.9
   
   # 或从官网下载安装包
   # https://www.python.org/downloads/macos/
   ```

#### 源码安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/CAJanus.git
cd CAJanus

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行环境检查
python check_environment.py

# 5. 启动应用
python gui_main.py
```

### Linux 详细安装

#### Ubuntu/Debian
```bash
# 1. 更新包管理器
sudo apt update

# 2. 安装Python和依赖
sudo apt install python3 python3-pip python3-venv git

# 3. 安装GUI依赖
sudo apt install python3-pyqt5 python3-pyqt5.qtwidgets

# 4. 克隆项目
git clone https://github.com/your-repo/CAJanus.git
cd CAJanus

# 5. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
pip install -r requirements.txt

# 7. 运行环境检查
python check_environment.py

# 8. 启动应用
python gui_main.py
```

#### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip git
sudo yum install python3-qt5

# Fedora
sudo dnf install python3 python3-pip git
sudo dnf install python3-qt5

# 后续步骤与Ubuntu相同
```

## ⚙️ 配置设置

### 首次运行配置
1. **权限设置**
   - Windows：以管理员身份运行
   - macOS/Linux：确保有sudo权限

2. **配置文件**
   - 默认配置：`config/default_config.yaml`
   - 用户配置：`config/user_config.yaml`（首次运行自动创建）

3. **日志目录**
   - 默认位置：`logs/`
   - 可在配置文件中修改

### 环境变量（可选）
```bash
# 设置配置目录
export CAJANUS_CONFIG_DIR="/path/to/config"

# 设置日志目录
export CAJANUS_LOG_DIR="/path/to/logs"

# 启用调试模式
export CAJANUS_DEBUG="true"
```

## 🧪 验证安装

### 自动检查
```bash
# 运行环境检查工具
python check_environment.py
```

### 手动验证
```bash
# 检查Python版本
python --version

# 检查依赖包
python -c "import PyQt5, psutil, yaml; print('所有依赖包已安装')"

# 测试GUI环境
python -c "from PyQt5.QtWidgets import QApplication; app = QApplication([]); print('GUI环境正常')"
```

## 🔄 更新升级

### 预编译包更新
1. 下载最新版本安装包
2. 卸载旧版本（可选）
3. 安装新版本

### 源码更新
```bash
# 进入项目目录
cd CAJanus

# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新运行环境检查
python check_environment.py
```

## 🗑️ 卸载

### Windows
- 通过"控制面板" > "程序和功能"卸载
- 或运行安装目录下的uninstall.exe

### macOS
- 将CAJanus.app从Applications文件夹移到废纸篓
- 清理配置文件：`rm -rf ~/Library/Application\ Support/CAJanus`

### Linux
- 删除AppImage文件
- 清理配置文件：`rm -rf ~/.local/share/CAJanus`

### 源码安装卸载
```bash
# 删除项目目录
rm -rf CAJanus

# 删除虚拟环境（如果单独创建）
rm -rf venv
```

## ❓ 常见问题

### 安装失败
**问题**：pip安装依赖失败
**解决**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 权限问题
**问题**：程序启动提示权限不足
**解决**：
- Windows：右键选择"以管理员身份运行"
- macOS/Linux：使用sudo运行或调整文件权限

### GUI显示问题
**问题**：界面显示异常或无法启动
**解决**：
```bash
# 检查显示环境变量（Linux）
echo $DISPLAY

# 安装额外的GUI库
sudo apt install python3-pyqt5.qtquick  # Ubuntu
```

## 📞 获取帮助

如果安装过程中遇到问题：
1. 查看 [故障排除指南](troubleshooting.md)
2. 搜索 [GitHub Issues](https://github.com/your-repo/CAJanus/issues)
3. 提交新的 [Issue](https://github.com/your-repo/CAJanus/issues/new)
4. 发送邮件至 support@example.com

---

**下一步**：[快速入门](quick-start.md) - 开始使用CAJanus
