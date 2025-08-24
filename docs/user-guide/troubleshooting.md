# 故障排除指南

本指南帮助您诊断和解决CAJanus使用过程中遇到的常见问题。

## 🔍 问题诊断流程

### 第一步：基础检查
1. **运行环境检查**：`python check_environment.py`
2. **查看系统状态**：在程序中检查系统状态标签页
3. **检查日志文件**：查看`logs/`目录下的日志文件
4. **验证权限**：确认具有必要的系统权限

### 第二步：问题分类
根据问题类型选择对应的解决方案：
- [启动问题](#启动问题)
- [功能问题](#功能问题)
- [界面问题](#界面问题)
- [性能问题](#性能问题)
- [权限问题](#权限问题)

---

## 启动问题

### 问题：程序无法启动

#### 症状
- 双击程序无反应
- 命令行启动报错
- 启动后立即崩溃

#### 诊断步骤
```bash
# 1. 检查Python版本
python --version

# 2. 验证依赖包
python -c "import PyQt5, psutil, yaml; print('依赖检查通过')"

# 3. 运行环境检查
python check_environment.py

# 4. 查看详细错误
python gui_main.py --debug
```

#### 解决方案
1. **Python版本问题**
   ```bash
   # 安装正确的Python版本
   # Windows: 从python.org下载
   # macOS: brew install python@3.9
   # Ubuntu: sudo apt install python3.9
   ```

2. **依赖包问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

3. **权限问题**
   ```bash
   # Windows: 以管理员身份运行
   # macOS/Linux: sudo python gui_main.py
   ```

### 问题：启动速度很慢

#### 症状
- 程序启动需要很长时间
- 启动画面停留时间过长

#### 解决方案
1. **系统优化**
   - 关闭不必要的后台程序
   - 确保有足够的可用内存
   - 使用SSD存储设备

2. **程序优化**
   ```yaml
   # 在config/user_config.yaml中设置
   performance:
     cache:
       enable_data_cache: true
     startup:
       skip_system_check: false  # 设为true可跳过启动检查
   ```

---

## 功能问题

### 问题：无法检测到网络适配器

#### 症状
- 网络适配器列表为空
- 显示"无可用适配器"

#### 诊断步骤
```bash
# Windows
ipconfig /all

# macOS
ifconfig -a

# Linux
ip addr show
```

#### 解决方案
1. **权限不足**
   - 以管理员身份重新启动程序
   - 检查用户账户权限

2. **驱动问题**
   - 更新网络适配器驱动
   - 重新安装网络适配器

3. **系统服务**
   ```bash
   # Windows: 重启网络服务
   net stop "Network Location Awareness"
   net start "Network Location Awareness"
   ```

### 问题：修改操作失败

#### 症状
- 修改MAC地址后没有生效
- 提示"修改失败"错误

#### 解决方案
1. **检查权限**
   - 确认具有管理员权限
   - 临时关闭防病毒软件

2. **网络适配器状态**
   - 确保适配器未被其他程序占用
   - 尝试禁用后重新启用适配器

3. **MAC地址格式**
   - 确保MAC地址格式正确（XX:XX:XX:XX:XX:XX）
   - 避免使用多播地址（第一个字节为奇数）

### 问题：备份创建失败

#### 症状
- 备份过程中断
- 提示"备份失败"错误

#### 解决方案
1. **磁盘空间**
   ```bash
   # 检查可用空间
   df -h  # Linux/macOS
   dir   # Windows
   ```

2. **文件权限**
   - 确保备份目录可写
   - 检查文件系统权限

3. **系统资源**
   - 关闭其他占用资源的程序
   - 等待系统负载降低后重试

---

## 界面问题

### 问题：界面显示异常

#### 症状
- 控件重叠或错位
- 字体显示异常
- 颜色显示不正确

#### 解决方案
1. **DPI设置**
   ```bash
   # 检查系统DPI设置
   # Windows: 显示设置 > 缩放与布局
   # macOS: 系统偏好设置 > 显示器
   ```

2. **显卡驱动**
   - 更新显卡驱动程序
   - 重启计算机

3. **程序设置**
   ```yaml
   # 在设置中调整
   ui:
     theme: "default"  # 尝试不同主题
     font_size: "standard"  # 调整字体大小
   ```

### 问题：程序无响应

#### 症状
- 界面冻结
- 无法点击按钮
- 程序假死

#### 解决方案
1. **强制结束**
   ```bash
   # 查找进程
   ps aux | grep python  # Linux/macOS
   tasklist | findstr python  # Windows
   
   # 结束进程
   kill -9 <PID>  # Linux/macOS
   taskkill /F /PID <PID>  # Windows
   ```

2. **系统资源**
   - 检查内存使用情况
   - 检查CPU使用率
   - 关闭其他程序释放资源

---

## 性能问题

### 问题：内存使用过高

#### 症状
- 程序占用大量内存
- 系统运行缓慢

#### 诊断
```bash
# 监控内存使用
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'内存使用: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

#### 解决方案
1. **配置优化**
   ```yaml
   performance:
     memory:
       max_memory_usage_mb: 256  # 限制内存使用
       enable_gc_optimization: true  # 启用垃圾回收优化
   ```

2. **功能调整**
   - 减少自动刷新频率
   - 关闭不必要的监控功能
   - 清理缓存数据

### 问题：响应速度慢

#### 症状
- 界面操作延迟
- 数据刷新缓慢

#### 解决方案
1. **性能优化**
   ```yaml
   performance:
     cache:
       enable_data_cache: true
     concurrency:
       enable_parallel_query: true
       max_worker_threads: 2
   ```

2. **系统优化**
   - 关闭不必要的后台服务
   - 增加系统内存
   - 使用更快的存储设备

---

## 权限问题

### 问题：权限不足错误

#### 症状
- 提示"需要管理员权限"
- 某些功能无法使用
- 访问被拒绝错误

#### 解决方案

#### Windows
```cmd
# 方法1: 右键以管理员身份运行
# 方法2: 使用runas命令
runas /user:Administrator "python gui_main.py"

# 方法3: 检查UAC设置
# 控制面板 > 用户账户 > 更改用户账户控制设置
```

#### macOS
```bash
# 使用sudo运行
sudo python gui_main.py

# 或者添加用户到admin组
sudo dseditgroup -o edit -a $USER -t user admin
```

#### Linux
```bash
# 使用sudo运行
sudo python gui_main.py

# 或者添加用户到sudo组
sudo usermod -aG sudo $USER
```

### 问题：文件访问权限

#### 症状
- 无法读取配置文件
- 无法写入日志文件
- 备份创建失败

#### 解决方案
```bash
# 检查文件权限
ls -la config/
ls -la logs/

# 修复权限
chmod 755 config/
chmod 644 config/*.yaml
chmod 755 logs/
chmod 644 logs/*.log
```

---

## 🛠️ 高级故障排除

### 收集诊断信息

#### 系统信息收集脚本
```bash
#!/bin/bash
# collect_info.sh

echo "=== CAJanus 诊断信息 ==="
echo "时间: $(date)"
echo "用户: $(whoami)"
echo "系统: $(uname -a)"
echo "Python: $(python --version)"
echo

echo "=== 依赖包检查 ==="
python -c "
import sys
packages = ['PyQt5', 'psutil', 'yaml']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg}')
    except ImportError:
        print(f'✗ {pkg}')
"
echo

echo "=== 权限检查 ==="
python check_environment.py
echo

echo "=== 最近错误日志 ==="
if [ -f "logs/error.log" ]; then
    tail -20 logs/error.log
else
    echo "无错误日志文件"
fi
```

### 重置程序状态

#### 完全重置脚本
```bash
#!/bin/bash
# reset_cajanus.sh

echo "重置CAJanus到默认状态..."

# 备份当前配置
if [ -f "config/user_config.yaml" ]; then
    cp config/user_config.yaml config/user_config.yaml.backup
    echo "已备份当前配置"
fi

# 删除用户配置
rm -f config/user_config.yaml

# 清空日志
rm -f logs/*.log

# 清空缓存
rm -rf cache/

echo "重置完成，请重新启动程序"
```

---

## 📞 获取更多帮助

### 自助资源
1. **查看日志**：`logs/`目录下的详细日志
2. **运行诊断**：`python check_environment.py`
3. **查看FAQ**：[faq.md](faq.md)
4. **用户手册**：[user-manual.md](user-manual.md)

### 社区支持
1. **GitHub Issues**：https://github.com/your-repo/CAJanus/issues
2. **讨论区**：https://github.com/your-repo/CAJanus/discussions
3. **邮件支持**：support@example.com

### 提交问题时请包含
- 操作系统和版本信息
- Python版本
- CAJanus版本
- 详细的错误描述和截图
- 相关的日志文件
- 问题复现步骤

---

**最后更新**：2024年1月15日  
**适用版本**：v1.0.0+
