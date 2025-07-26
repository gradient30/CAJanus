# 贡献指南 / Contributing Guide

感谢您对CAJanus项目的关注！我们欢迎社区的贡献，无论是代码、文档、测试还是反馈建议。

## 🤝 如何贡献

### 贡献类型

1. **🐛 Bug报告**：发现并报告软件缺陷
2. **💡 功能建议**：提出新功能或改进建议
3. **📝 文档改进**：完善文档、教程和示例
4. **🔧 代码贡献**：修复bug、实现新功能
5. **🧪 测试贡献**：编写测试用例、进行测试
6. **🌍 翻译贡献**：添加新语言支持或改进翻译

### 贡献流程

1. **Fork项目**：点击GitHub页面右上角的"Fork"按钮
2. **克隆仓库**：`git clone https://github.com/your-username/CAJanus.git`
3. **创建分支**：`git checkout -b feature/your-feature-name`
4. **进行开发**：按照开发规范进行代码编写
5. **提交更改**：`git commit -m "Add: your feature description"`
6. **推送分支**：`git push origin feature/your-feature-name`
7. **创建PR**：在GitHub上创建Pull Request

## 📋 开发环境设置

### 环境要求

- Python 3.8+
- Git
- 支持的操作系统：Windows 10+, macOS 10.14+, Ubuntu 18.04+

### 设置步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/CAJanus.git
cd CAJanus

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 安装pre-commit钩子
pre-commit install

# 6. 运行测试确保环境正常
python -m pytest tests/ -v
```

## 📝 开发规范

### 代码风格

我们使用以下工具确保代码质量：

- **Black**：代码格式化
- **isort**：导入排序
- **flake8**：代码检查
- **pylint**：代码质量分析
- **mypy**：类型检查

```bash
# 运行代码格式化
black src/ tests/
isort src/ tests/

# 运行代码检查
flake8 src/ tests/
pylint src/
mypy src/
```

### 命名规范

- **类名**：使用PascalCase，如`ConfigManager`
- **函数和变量**：使用snake_case，如`get_config_value`
- **常量**：使用UPPER_SNAKE_CASE，如`MAX_RETRY_COUNT`
- **私有成员**：使用下划线前缀，如`_private_method`

### 文档字符串

使用Google风格的文档字符串：

```python
def example_function(param1: str, param2: int) -> bool:
    """示例函数的简短描述。
    
    更详细的描述可以写在这里，解释函数的用途、
    算法或其他重要信息。
    
    Args:
        param1: 第一个参数的描述
        param2: 第二个参数的描述
        
    Returns:
        返回值的描述
        
    Raises:
        ValueError: 当参数无效时抛出
        
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    return True
```

## 🧪 测试规范

### 测试结构

```
tests/
├── unit/                   # 单元测试
├── integration/            # 集成测试
├── ui/                     # UI测试
├── performance/            # 性能测试
└── fixtures/               # 测试数据
```

### 测试命名

- 测试类：`Test + 被测试的类名`，如`TestConfigManager`
- 测试方法：`test_ + 测试场景描述`，如`test_get_config_with_valid_key`

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_config_manager.py -v

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html

# 运行性能测试
python -m pytest tests/performance/ -v
```

## 📄 提交规范

### 提交信息格式

使用Conventional Commits格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 提交类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD相关

### 提交示例

```bash
feat(ui): 添加响应式布局支持

- 实现屏幕尺寸自动检测
- 添加DPI缩放支持
- 优化小屏幕设备显示

Closes #123
```

## 🔍 Pull Request规范

### PR标题

使用清晰、描述性的标题：
- ✅ `feat: 添加MAC地址修改功能`
- ✅ `fix: 修复配置文件加载错误`
- ❌ `更新代码`
- ❌ `修复bug`

### PR描述

包含以下信息：

```markdown
## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他

## 变更描述
简要描述此PR的目的和实现方式。

## 测试
- [ ] 添加了新的测试用例
- [ ] 所有现有测试通过
- [ ] 手动测试通过

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的文档
- [ ] 更新了相关的README或文档
- [ ] 没有引入新的警告或错误

## 相关Issue
Closes #123
```

### 代码审查

所有PR都需要经过代码审查：

1. **自动检查**：CI/CD会自动运行测试和代码检查
2. **人工审查**：至少需要一名维护者的审查
3. **反馈处理**：及时回应审查意见并进行修改

## 🐛 Bug报告

### 报告模板

```markdown
## Bug描述
简要描述遇到的问题。

## 复现步骤
1. 打开应用程序
2. 点击"设备指纹"标签页
3. 点击"刷新"按钮
4. 观察错误

## 预期行为
描述你期望发生的情况。

## 实际行为
描述实际发生的情况。

## 环境信息
- 操作系统：Windows 11
- Python版本：3.9.7
- 应用版本：1.0.0
- 其他相关信息

## 附加信息
- 错误截图
- 日志文件
- 其他有助于诊断的信息
```

## 💡 功能建议

### 建议模板

```markdown
## 功能描述
简要描述建议的新功能。

## 使用场景
描述这个功能的使用场景和目标用户。

## 详细设计
如果有具体的设计想法，请详细描述。

## 替代方案
是否考虑过其他实现方式？

## 优先级
- [ ] 高：核心功能，急需实现
- [ ] 中：有用的功能，可以考虑
- [ ] 低：nice-to-have功能
```

## 🌍 国际化贡献

### 添加新语言

1. 在`resources/i18n/`目录下创建新的语言文件
2. 参考现有的`zh_CN.json`文件结构
3. 翻译所有文本条目
4. 在`SupportedLanguage`枚举中添加新语言
5. 测试新语言的显示效果

### 改进现有翻译

1. 编辑对应的语言文件
2. 确保翻译准确、自然
3. 考虑文化差异和本地化需求
4. 测试翻译效果

## 📞 联系方式

如有任何问题或建议，请通过以下方式联系我们：

- **GitHub Issues**：https://github.com/your-repo/CAJanus/issues
- **GitHub Discussions**：https://github.com/your-repo/CAJanus/discussions
- **邮箱**：contribute@example.com

## 🏆 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里会自动生成贡献者列表 -->

## 📜 行为准则

参与本项目即表示您同意遵守我们的[行为准则](CODE_OF_CONDUCT.md)。我们致力于为所有人提供友好、安全、包容的环境。

---

再次感谢您对CAJanus项目的贡献！🎉
