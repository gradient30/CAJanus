# 开发指南

本指南为CAJanus项目的开发者提供详细的开发环境搭建、代码规范和贡献流程说明。

## 📋 目录

1. [开发环境搭建](#开发环境搭建)
2. [项目结构](#项目结构)
3. [开发工作流](#开发工作流)
4. [代码规范](#代码规范)
5. [测试指南](#测试指南)
6. [调试技巧](#调试技巧)

---

## 开发环境搭建

### 前置要求

#### 系统要求
- **操作系统**：Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**：3.8+ (推荐3.9+)
- **Git**：2.20+
- **内存**：8GB+ (推荐16GB)
- **存储**：5GB+ 可用空间

#### 必需工具
```bash
# Python包管理
pip >= 21.0

# 版本控制
git >= 2.20

# 代码编辑器 (推荐)
# - Visual Studio Code
# - PyCharm
# - Vim/Neovim
```

### 环境搭建步骤

#### 1. 克隆项目
```bash
# 克隆主仓库
git clone https://github.com/your-repo/CAJanus.git
cd CAJanus

# 或者克隆你的fork
git clone https://github.com/your-username/CAJanus.git
cd CAJanus

# 添加上游仓库
git remote add upstream https://github.com/your-repo/CAJanus.git
```

#### 2. 创建开发环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 升级pip
python -m pip install --upgrade pip
```

#### 3. 安装依赖
```bash
# 安装运行时依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 验证安装
python check_environment.py
```

#### 4. 配置开发工具
```bash
# 安装pre-commit钩子
pre-commit install

# 配置Git钩子
git config core.hooksPath .githooks
```

### IDE配置

#### Visual Studio Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.unittestEnabled": true,
    "python.testing.unittestArgs": [
        "-v", "-s", "./tests", "-p", "test_*.py"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true
    }
}
```

#### PyCharm
1. 打开项目目录
2. 配置Python解释器：`venv/bin/python`
3. 启用代码检查：Pylint, Black, isort
4. 配置测试运行器：unittest

---

## 项目结构

### 目录结构
```
CAJanus/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   ├── platforms/         # 平台特定实现
│   ├── ui/                # 用户界面
│   └── __init__.py
├── tests/                 # 测试代码
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── fixtures/          # 测试数据
├── config/                # 配置文件
├── docs/                  # 文档
├── resources/             # 资源文件
├── logs/                  # 日志文件
├── requirements.txt       # 运行依赖
├── requirements-dev.txt   # 开发依赖
└── gui_main.py           # 程序入口
```

### 核心模块说明

#### src/core/
- `config_manager.py` - 配置管理
- `logger.py` - 日志系统
- `platform_factory.py` - 平台工厂
- `i18n_manager.py` - 国际化管理

#### src/platforms/
- `windows/` - Windows平台实现
- `macos/` - macOS平台实现
- `linux/` - Linux平台实现
- `base.py` - 平台基类

#### src/ui/
- `main_window.py` - 主窗口
- `widgets/` - 自定义控件
- `dialogs/` - 对话框
- `styles/` - 样式文件

---

## 开发工作流

### Git工作流

#### 分支策略
```
main                 # 主分支，稳定版本
├── develop         # 开发分支
├── feature/xxx     # 功能分支
├── hotfix/xxx      # 热修复分支
└── release/xxx     # 发布分支
```

#### 开发流程
```bash
# 1. 同步主分支
git checkout main
git pull upstream main

# 2. 创建功能分支
git checkout -b feature/new-feature

# 3. 开发和提交
git add .
git commit -m "feat: add new feature"

# 4. 推送分支
git push origin feature/new-feature

# 5. 创建Pull Request
# 在GitHub上创建PR到develop分支
```

### 提交规范

#### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型说明
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 示例
```bash
feat(ui): 添加响应式布局支持

- 实现屏幕尺寸自动检测
- 添加DPI缩放支持
- 优化小屏幕设备显示

Closes #123
```

---

## 代码规范

### Python代码风格

#### 基本规范
- 遵循 PEP 8 代码风格指南
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 Pylint 进行代码检查

#### 命名规范
```python
# 类名：PascalCase
class ConfigManager:
    pass

# 函数和变量：snake_case
def get_config_value():
    config_file_path = "config.yaml"

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# 私有成员：下划线前缀
class MyClass:
    def __init__(self):
        self._private_var = None
        self.__very_private_var = None
```

#### 文档字符串
```python
def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
    """修改网络适配器的MAC地址
    
    Args:
        adapter_id: 网络适配器ID
        new_mac: 新的MAC地址，格式为 XX:XX:XX:XX:XX:XX
        
    Returns:
        bool: 修改成功返回True，失败返回False
        
    Raises:
        ValueError: 当MAC地址格式无效时
        PermissionError: 当权限不足时
        
    Example:
        >>> engine = WindowsFingerprintEngine()
        >>> success = engine.modify_mac_address("0001", "00:11:22:33:44:55")
        >>> print(success)
        True
    """
```

#### 类型提示
```python
from typing import List, Dict, Optional, Union

def process_adapters(
    adapters: List[NetworkAdapter],
    config: Dict[str, Any]
) -> Optional[ProcessResult]:
    """处理网络适配器列表"""
    pass
```

### 代码质量检查

#### 运行检查工具
```bash
# 代码格式化
black src/ tests/
isort src/ tests/

# 代码检查
flake8 src/ tests/
pylint src/

# 类型检查
mypy src/

# 安全检查
bandit -r src/
```

#### 自动化检查
```bash
# 运行所有检查
make lint

# 或使用pre-commit
pre-commit run --all-files
```

---

## 测试指南

### 测试结构

#### 测试分类
```
tests/
├── unit/                   # 单元测试
│   ├── test_config_manager.py
│   ├── test_platform_factory.py
│   └── ...
├── integration/            # 集成测试
│   ├── test_core_integration.py
│   ├── test_ui_integration.py
│   └── ...
├── ui/                     # UI测试
│   ├── test_main_window.py
│   └── ...
└── fixtures/               # 测试数据
    ├── config/
    └── data/
```

#### 测试命名规范
```python
class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def test_get_config_with_valid_key(self):
        """测试获取有效配置键"""
        pass
    
    def test_get_config_with_invalid_key_should_return_default(self):
        """测试获取无效配置键应返回默认值"""
        pass
```

### 运行测试

#### 基本测试命令
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/unit/test_config_manager.py -v

# 运行特定测试方法
python -m pytest tests/unit/test_config_manager.py::TestConfigManager::test_get_config -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

#### 测试配置
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

### 编写测试

#### 单元测试示例
```python
import unittest
from unittest.mock import Mock, patch
from src.core.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        """测试初始化"""
        self.config_manager = ConfigManager("test_config.yaml")
    
    def tearDown(self):
        """测试清理"""
        # 清理测试文件
        pass
    
    def test_get_config_returns_correct_value(self):
        """测试获取配置返回正确值"""
        # Arrange
        expected_value = "test_value"
        self.config_manager.config = {"test_key": expected_value}
        
        # Act
        result = self.config_manager.get_config("test_key")
        
        # Assert
        self.assertEqual(result, expected_value)
    
    @patch('src.core.config_manager.yaml.safe_load')
    def test_load_config_handles_file_error(self, mock_yaml_load):
        """测试加载配置处理文件错误"""
        # Arrange
        mock_yaml_load.side_effect = FileNotFoundError()
        
        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            self.config_manager.load_config()
```

#### UI测试示例
```python
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import unittest

from src.ui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """测试初始化"""
        self.window = MainWindow()
    
    def tearDown(self):
        """测试清理"""
        self.window.close()
    
    def test_window_title(self):
        """测试窗口标题"""
        expected_title = "CAJanus - 设备指纹识别与修改工具"
        self.assertEqual(self.window.windowTitle(), expected_title)
    
    def test_tab_switching(self):
        """测试标签页切换"""
        # 点击第二个标签页
        QTest.mouseClick(
            self.window.tab_widget.tabBar().tabButton(1, 0),
            Qt.LeftButton
        )
        
        # 验证当前标签页
        self.assertEqual(self.window.tab_widget.currentIndex(), 1)
```

---

## 调试技巧

### 日志调试

#### 配置调试日志
```python
import logging
from src.core.logger import get_logger

# 获取调试日志器
logger = get_logger("debug")
logger.setLevel(logging.DEBUG)

# 添加调试信息
logger.debug(f"处理适配器: {adapter.name}")
logger.debug(f"当前配置: {config}")
```

#### 启用调试模式
```bash
# 环境变量方式
export CAJANUS_DEBUG=true
python gui_main.py

# 命令行参数方式
python gui_main.py --debug

# 配置文件方式
# 在config/user_config.yaml中设置
debug: true
log_level: "DEBUG"
```

### 性能调试

#### 性能分析
```python
import cProfile
import pstats

# 性能分析装饰器
def profile_function(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result
    return wrapper

# 使用示例
@profile_function
def slow_function():
    # 需要分析的函数
    pass
```

#### 内存调试
```python
import tracemalloc
import psutil
import os

# 启用内存跟踪
tracemalloc.start()

# 获取内存使用情况
def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # MB

# 内存快照
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

### GUI调试

#### Qt调试工具
```python
# 启用Qt调试输出
import os
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*.debug=true'

# 显示控件边界
from PyQt5.QtWidgets import QApplication
app = QApplication.instance()
app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
```

#### 事件调试
```python
from PyQt5.QtCore import QEvent

class DebugEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            print(f"鼠标点击: {obj.objectName()}")
        return super().eventFilter(obj, event)

# 安装事件过滤器
debug_filter = DebugEventFilter()
widget.installEventFilter(debug_filter)
```

---

## 📚 参考资源

### 开发文档
- [架构设计](architecture.md) - 系统架构和设计原理
- [API参考](api-reference.md) - 接口文档和示例
- [文档规范](documentation-standards.md) - 文档编写规范

### 外部资源
- [Python官方文档](https://docs.python.org/)
- [PyQt5文档](https://doc.qt.io/qtforpython/)
- [pytest文档](https://docs.pytest.org/)

### 社区资源
- [GitHub仓库](https://github.com/your-repo/CAJanus)
- [讨论区](https://github.com/your-repo/CAJanus/discussions)
- [Issue跟踪](https://github.com/your-repo/CAJanus/issues)

---

**最后更新**：2024年1月15日  
**适用版本**：v1.0.0+
