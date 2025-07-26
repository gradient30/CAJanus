# 配置管理指南

> ⚙️ **配置文件和参数说明** - CAJanus配置系统的详细说明和最佳实践

## 📋 目录

1. [配置概览](#配置概览)
2. [配置文件结构](#配置文件结构)
3. [配置参数详解](#配置参数详解)
4. [环境变量](#环境变量)
5. [配置验证](#配置验证)
6. [最佳实践](#最佳实践)

---

## 配置概览

### 配置文件层次
CAJanus使用分层配置系统，按优先级从高到低：

```
环境变量 > 用户配置 > 默认配置
    ↓         ↓         ↓
  运行时    user_config  default_config
```

### 配置文件位置
```
config/
├── default_config.yaml    # 默认配置（不要修改）
├── user_config.yaml       # 用户配置（首次运行自动创建）
├── production_config.yaml # 生产环境配置模板
└── development_config.yaml # 开发环境配置模板
```

### 配置加载顺序
1. 加载默认配置 (`default_config.yaml`)
2. 加载用户配置 (`user_config.yaml`)，覆盖默认值
3. 应用环境变量，覆盖文件配置
4. 验证配置完整性和有效性

---

## 配置文件结构

### 完整配置示例
```yaml
# CAJanus 配置文件
# 版本: 1.0.0

# 应用程序基础配置
app:
  name: "CAJanus"
  version: "1.0.0"
  debug: false
  environment: "production"  # development, testing, production
  
  # 日志配置
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_to_file: true
  log_to_console: true
  
  # 语言和区域设置
  language: "zh_CN"  # zh_CN, en_US, zh_TW, ja_JP
  timezone: "Asia/Shanghai"
  
  # 启动配置
  startup:
    check_updates: true
    show_splash: true
    restore_window_state: true
    auto_check_permissions: true

# 用户界面配置
ui:
  # 主题设置
  theme: "default"  # default, dark, high_contrast
  font_family: "Microsoft YaHei"
  font_size: 9
  
  # 窗口设置
  window:
    width: 1200
    height: 800
    min_width: 800
    min_height: 600
    remember_size: true
    remember_position: true
    start_maximized: false
  
  # 界面行为
  behavior:
    auto_refresh_interval: 30  # 秒
    show_tooltips: true
    confirm_exit: true
    minimize_to_tray: false
  
  # 响应式布局
  responsive:
    enable: true
    auto_detect_dpi: true
    scale_factor: 1.0  # 手动DPI缩放因子
  
  # 无障碍功能
  accessibility:
    level: "none"  # none, low_vision, high_contrast, keyboard_nav, screen_reader
    enable_keyboard_nav: false
    high_contrast_mode: false
    large_fonts: false

# 功能配置
features:
  # 设备指纹识别
  fingerprint:
    enable_network_adapters: true
    enable_hardware_info: true
    enable_system_info: true
    cache_results: true
    cache_expire_seconds: 300
  
  # 修改功能
  modification:
    enable_mac_modification: true
    enable_guid_modification: true
    require_confirmation: true
    create_backup_before_modify: true
  
  # 备份功能
  backup:
    auto_backup: true
    backup_before_modify: true
    max_backup_count: 10
    compress_backups: true
    backup_location: "./backups"
  
  # 教育功能
  education:
    show_principles: true
    show_warnings: true
    show_legal_notices: true
    enable_learning_mode: false

# 安全配置
security:
  # 操作确认
  confirmation:
    enable_three_level: true
    require_admin_approval: false
    timeout_seconds: 300
    
    # 确认级别设置
    levels:
      basic:
        show_operation_info: true
        show_risk_level: true
      risk:
        show_detailed_risks: true
        require_risk_acknowledgment: true
        show_recovery_options: true
      final:
        require_confirmation_code: true
        show_final_warnings: true
        require_explicit_consent: true
  
  # 访问控制
  access_control:
    enable_ip_whitelist: false
    allowed_ips: []
    enable_time_restrictions: false
    allowed_hours: "09:00-18:00"
  
  # 审计日志
  audit:
    enable: true
    log_all_operations: true
    log_configuration_changes: true
    log_file: "logs/audit.log"
    max_log_size_mb: 100
    max_log_files: 10

# 性能配置
performance:
  # 缓存设置
  cache:
    enable_data_cache: true
    cache_size_mb: 50
    cache_expire_seconds: 600
    clear_cache_on_exit: false
  
  # 并发设置
  concurrency:
    enable_parallel_query: true
    max_worker_threads: 4
    query_timeout_seconds: 30
  
  # 内存管理
  memory:
    max_memory_usage_mb: 512
    enable_gc_optimization: true
    gc_threshold_mb: 400
    monitor_memory_usage: false
  
  # 网络设置
  network:
    connection_timeout: 10
    read_timeout: 30
    max_retries: 3
    retry_delay: 1

# 日志配置
logging:
  # 基础设置
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  # 日志文件
  files:
    app_log: "logs/app.log"
    error_log: "logs/error.log"
    debug_log: "logs/debug.log"
    audit_log: "logs/audit.log"
  
  # 日志轮转
  rotation:
    max_file_size_mb: 10
    max_file_count: 5
    compress_old_files: true
  
  # 控制台输出
  console:
    enable: true
    level: "INFO"
    colored_output: true
  
  # 远程日志（可选）
  remote:
    enable: false
    server: "log.example.com"
    port: 514
    protocol: "udp"  # udp, tcp

# 数据存储配置
storage:
  # 数据目录
  data_dir: "./data"
  config_dir: "./config"
  cache_dir: "./cache"
  temp_dir: "./temp"
  
  # 数据库配置（如果使用）
  database:
    enable: false
    type: "sqlite"  # sqlite, postgresql, mysql
    host: "localhost"
    port: 5432
    name: "cajanus"
    user: "cajanus_user"
    password: ""
    
  # 文件存储
  files:
    auto_cleanup: true
    cleanup_interval_hours: 24
    max_temp_file_age_hours: 48

# 网络配置
network:
  # HTTP设置
  http:
    timeout: 30
    max_redirects: 5
    verify_ssl: true
    user_agent: "CAJanus/1.0.0"
  
  # 代理设置
  proxy:
    enable: false
    http_proxy: ""
    https_proxy: ""
    no_proxy: "localhost,127.0.0.1"
  
  # DNS设置
  dns:
    servers: []
    timeout: 5

# 插件配置
plugins:
  # 插件系统
  enable: false
  plugin_dir: "./plugins"
  auto_load: true
  
  # 已启用的插件
  enabled_plugins: []
  
  # 插件配置
  plugin_configs: {}

# 开发和调试配置
development:
  # 调试设置
  debug_mode: false
  verbose_logging: false
  show_debug_info: false
  
  # 性能分析
  enable_profiling: false
  profile_output_dir: "./profiles"
  
  # 测试设置
  test_mode: false
  mock_system_calls: false
  
  # 开发工具
  enable_dev_tools: false
  hot_reload: false

# 实验性功能
experimental:
  # 新功能开关
  enable_experimental_features: false
  
  # 具体实验功能
  features:
    ai_assistance: false
    cloud_sync: false
    advanced_analytics: false
    mobile_support: false
```

---

## 配置参数详解

### 应用程序配置 (app)

#### 基础参数
```yaml
app:
  name: "CAJanus"              # 应用程序名称
  version: "1.0.0"             # 版本号
  debug: false                 # 调试模式开关
  environment: "production"    # 运行环境
  log_level: "INFO"           # 日志级别
  language: "zh_CN"           # 界面语言
```

**参数说明**：
- `debug`: 启用后会显示详细的调试信息
- `environment`: 影响默认配置和行为模式
- `log_level`: 控制日志输出的详细程度
- `language`: 支持的语言代码见国际化章节

#### 启动配置
```yaml
startup:
  check_updates: true          # 启动时检查更新
  show_splash: true           # 显示启动画面
  restore_window_state: true  # 恢复窗口状态
  auto_check_permissions: true # 自动检查权限
```

### 用户界面配置 (ui)

#### 主题设置
```yaml
ui:
  theme: "default"            # 界面主题
  font_family: "Microsoft YaHei"  # 字体族
  font_size: 9               # 字体大小
```

**可用主题**：
- `default`: 默认浅色主题
- `dark`: 深色主题
- `high_contrast`: 高对比度主题

#### 窗口设置
```yaml
window:
  width: 1200                # 窗口宽度
  height: 800                # 窗口高度
  min_width: 800             # 最小宽度
  min_height: 600            # 最小高度
  remember_size: true        # 记住窗口大小
  remember_position: true    # 记住窗口位置
  start_maximized: false     # 启动时最大化
```

#### 响应式布局
```yaml
responsive:
  enable: true               # 启用响应式布局
  auto_detect_dpi: true      # 自动检测DPI
  scale_factor: 1.0          # 手动缩放因子
```

### 功能配置 (features)

#### 设备指纹识别
```yaml
fingerprint:
  enable_network_adapters: true  # 启用网络适配器识别
  enable_hardware_info: true     # 启用硬件信息识别
  enable_system_info: true       # 启用系统信息识别
  cache_results: true            # 缓存识别结果
  cache_expire_seconds: 300      # 缓存过期时间
```

#### 修改功能
```yaml
modification:
  enable_mac_modification: true     # 启用MAC地址修改
  enable_guid_modification: true    # 启用GUID修改
  require_confirmation: true        # 需要确认
  create_backup_before_modify: true # 修改前创建备份
```

### 安全配置 (security)

#### 三级确认系统
```yaml
confirmation:
  enable_three_level: true    # 启用三级确认
  require_admin_approval: false # 需要管理员批准
  timeout_seconds: 300       # 确认超时时间
  
  levels:
    basic:
      show_operation_info: true    # 显示操作信息
      show_risk_level: true        # 显示风险级别
    risk:
      show_detailed_risks: true    # 显示详细风险
      require_risk_acknowledgment: true # 需要风险确认
    final:
      require_confirmation_code: true   # 需要确认码
      show_final_warnings: true        # 显示最终警告
```

### 性能配置 (performance)

#### 缓存设置
```yaml
cache:
  enable_data_cache: true     # 启用数据缓存
  cache_size_mb: 50          # 缓存大小限制
  cache_expire_seconds: 600  # 缓存过期时间
  clear_cache_on_exit: false # 退出时清理缓存
```

#### 并发设置
```yaml
concurrency:
  enable_parallel_query: true  # 启用并行查询
  max_worker_threads: 4        # 最大工作线程数
  query_timeout_seconds: 30    # 查询超时时间
```

---

## 环境变量

### 系统环境变量
```bash
# 基础配置
export CAJANUS_ENV="production"
export CAJANUS_DEBUG="false"
export CAJANUS_LOG_LEVEL="INFO"

# 目录配置
export CAJANUS_CONFIG_DIR="/etc/cajanus"
export CAJANUS_DATA_DIR="/var/lib/cajanus"
export CAJANUS_LOG_DIR="/var/log/cajanus"
export CAJANUS_CACHE_DIR="/var/cache/cajanus"

# 性能配置
export CAJANUS_MAX_MEMORY_MB="512"
export CAJANUS_MAX_WORKERS="4"
export CAJANUS_CACHE_SIZE_MB="50"

# 安全配置
export CAJANUS_ENABLE_AUDIT="true"
export CAJANUS_REQUIRE_CONFIRMATION="true"
export CAJANUS_ADMIN_APPROVAL="false"

# 网络配置
export CAJANUS_HTTP_PROXY="http://proxy.company.com:8080"
export CAJANUS_HTTPS_PROXY="http://proxy.company.com:8080"
export CAJANUS_NO_PROXY="localhost,127.0.0.1"

# 数据库配置（如果使用）
export CAJANUS_DB_HOST="localhost"
export CAJANUS_DB_PORT="5432"
export CAJANUS_DB_NAME="cajanus"
export CAJANUS_DB_USER="cajanus_user"
export CAJANUS_DB_PASSWORD="secure_password"
```

### 环境变量优先级
环境变量会覆盖配置文件中的对应设置：

```python
# 环境变量映射规则
CAJANUS_DEBUG → app.debug
CAJANUS_LOG_LEVEL → app.log_level
CAJANUS_MAX_MEMORY_MB → performance.memory.max_memory_usage_mb
CAJANUS_ENABLE_AUDIT → security.audit.enable
```

---

## 配置验证

### 自动验证
程序启动时会自动验证配置：

```python
# 验证配置完整性
def validate_config(config: Dict[str, Any]) -> List[str]:
    """验证配置并返回错误列表"""
    errors = []
    
    # 检查必需配置
    required_keys = [
        'app.name',
        'app.version',
        'ui.theme',
        'security.confirmation.enable_three_level'
    ]
    
    for key in required_keys:
        if not get_nested_value(config, key):
            errors.append(f"缺少必需配置: {key}")
    
    return errors
```

### 手动验证
使用配置验证工具：

```bash
# 验证配置文件
python -m src.tools.validate_config config/user_config.yaml

# 验证生产环境配置
python -m src.tools.validate_config config/production_config.yaml --strict
```

### 配置检查清单

#### 基础检查
- [ ] 所有必需配置项已设置
- [ ] 配置值类型正确
- [ ] 数值范围在有效区间内
- [ ] 文件路径存在且可访问

#### 安全检查
- [ ] 三级确认系统已启用
- [ ] 审计日志已启用
- [ ] 敏感配置已加密
- [ ] 访问控制配置正确

#### 性能检查
- [ ] 内存限制设置合理
- [ ] 缓存配置优化
- [ ] 并发参数适当
- [ ] 超时设置合理

---

## 最佳实践

### 配置管理最佳实践

#### 1. 环境分离
```yaml
# 开发环境
app:
  debug: true
  log_level: "DEBUG"
  
# 生产环境
app:
  debug: false
  log_level: "INFO"
```

#### 2. 敏感信息保护
```yaml
# 使用环境变量存储敏感信息
database:
  password: "${DB_PASSWORD}"
  
# 或使用配置文件加密
security:
  encryption_key: "${ENCRYPTION_KEY}"
```

#### 3. 配置版本控制
```bash
# 版本控制配置模板，不包含敏感信息
git add config/default_config.yaml
git add config/production_config.yaml.template

# 不要提交包含敏感信息的配置
echo "config/user_config.yaml" >> .gitignore
echo "config/production_config.yaml" >> .gitignore
```

#### 4. 配置文档化
```yaml
# 在配置文件中添加注释
ui:
  theme: "default"  # 可选值: default, dark, high_contrast
  font_size: 9      # 范围: 8-16
```

### 部署配置建议

#### 开发环境
```yaml
app:
  debug: true
  log_level: "DEBUG"
  
performance:
  cache:
    enable_data_cache: false  # 开发时禁用缓存
  
logging:
  console:
    enable: true
    colored_output: true
```

#### 测试环境
```yaml
app:
  debug: false
  log_level: "INFO"
  
security:
  confirmation:
    timeout_seconds: 60  # 测试时缩短超时
  
performance:
  memory:
    max_memory_usage_mb: 256  # 测试环境资源限制
```

#### 生产环境
```yaml
app:
  debug: false
  log_level: "WARNING"
  
security:
  confirmation:
    enable_three_level: true
  audit:
    enable: true
    log_all_operations: true
  
performance:
  memory:
    max_memory_usage_mb: 1024
  cache:
    enable_data_cache: true
```

### 配置优化建议

#### 性能优化
```yaml
# 根据硬件配置调整
performance:
  concurrency:
    max_worker_threads: 8  # CPU核心数
  memory:
    max_memory_usage_mb: 2048  # 可用内存的25%
  cache:
    cache_size_mb: 200  # 内存的10%
```

#### 安全加固
```yaml
security:
  confirmation:
    enable_three_level: true
    require_admin_approval: true  # 生产环境建议启用
  access_control:
    enable_ip_whitelist: true
    allowed_ips:
      - "192.168.1.0/24"
  audit:
    enable: true
    log_all_operations: true
```

---

## 📚 相关文档

- [部署指南](deployment-guide.md) - 生产环境部署
- [监控运维](monitoring.md) - 监控和维护指南
- [故障排除](../user-guide/troubleshooting.md) - 配置问题排查

---

**最后更新**：2024年1月15日  
**配置版本**：v1.0.0
