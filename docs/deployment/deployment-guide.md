# 部署指南

本指南提供CAJanus在不同环境中的部署方案和最佳实践。

## 📋 目录

1. [部署概述](#部署概述)
2. [环境准备](#环境准备)
3. [部署方式](#部署方式)
4. [配置管理](#配置管理)
5. [监控运维](#监控运维)
6. [故障处理](#故障处理)
7. [安全配置](#安全配置)

---

## 部署概述

### 部署架构选择

#### 单机部署
**适用场景**：
- 个人学习和研究
- 小型教学环境
- 概念验证和测试

**特点**：
- 部署简单，维护成本低
- 资源需求最小
- 适合快速上手

#### 实验室部署
**适用场景**：
- 教学实验室
- 研究机构
- 培训中心

**特点**：
- 支持多用户并发
- 集中管理和配置
- 统一的监控和日志

#### 企业部署
**适用场景**：
- 大型教育机构
- 企业培训
- 安全研究团队

**特点**：
- 高可用性设计
- 完整的安全控制
- 详细的审计和合规

### 系统要求

#### 最低配置
```yaml
硬件要求:
  CPU: 双核 2.0GHz
  内存: 4GB RAM
  存储: 10GB 可用空间
  网络: 100Mbps

软件要求:
  操作系统: Windows 10+, macOS 10.14+, Ubuntu 18.04+
  Python: 3.8+
  权限: 管理员/root权限
```

#### 推荐配置
```yaml
硬件要求:
  CPU: 四核 3.0GHz 或更高
  内存: 8GB RAM 或更多
  存储: 50GB SSD
  网络: 1Gbps

软件要求:
  操作系统: 最新稳定版本
  Python: 3.9+
  监控: 系统监控工具
```

---

## 环境准备

### 系统环境配置

#### Windows环境
```powershell
# 1. 启用必要的Windows功能
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

# 2. 配置PowerShell执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. 安装Chocolatey包管理器
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# 4. 安装Python
choco install python --version=3.9.13

# 5. 安装Git
choco install git
```

#### Linux环境
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3-pip git curl wget

# 安装GUI依赖
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwidgets

# CentOS/RHEL
sudo yum install -y python39 python39-pip git
sudo yum install -y python3-qt5

# 创建系统用户
sudo useradd -m -s /bin/bash cajanus
sudo usermod -aG sudo cajanus
```

#### macOS环境
```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python
brew install python@3.9

# 安装Git
brew install git

# 安装系统依赖
brew install qt5
```

### 网络配置

#### 防火墙配置
```bash
# Linux (UFW)
sudo ufw allow ssh
sudo ufw allow from 192.168.1.0/24  # 允许内网访问
sudo ufw enable

# Windows防火墙
# 通过Windows Defender防火墙设置允许程序通过防火墙
```

#### 代理配置（如需要）
```bash
# 设置HTTP代理
export http_proxy=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080

# 设置pip代理
pip config set global.proxy http://proxy.company.com:8080
```

---

## 部署方式

### 方式一：源码部署

#### 标准部署流程
```bash
# 1. 创建部署目录
sudo mkdir -p /opt/cajanus
sudo chown cajanus:cajanus /opt/cajanus
cd /opt/cajanus

# 2. 克隆源码
git clone https://github.com/your-repo/CAJanus.git .
git checkout v1.0.0  # 使用稳定版本

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 5. 配置应用
cp config/default_config.yaml config/user_config.yaml
# 编辑配置文件...

# 6. 运行环境检查
python check_environment.py

# 7. 创建启动脚本
cat > start_cajanus.sh << 'EOF'
#!/bin/bash
cd /opt/cajanus
source venv/bin/activate
python gui_main.py "$@"
EOF

chmod +x start_cajanus.sh
```

#### 系统服务配置（可选）
```ini
# /etc/systemd/system/cajanus.service
[Unit]
Description=CAJanus Device Fingerprint Tool
After=network.target

[Service]
Type=simple
User=cajanus
Group=cajanus
WorkingDirectory=/opt/cajanus
Environment=PATH=/opt/cajanus/venv/bin
ExecStart=/opt/cajanus/venv/bin/python gui_main.py --service
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 方式二：容器化部署

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxrender1 \
    libxrandr2 \
    libxss1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN useradd -m -u 1000 cajanus

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置权限
RUN chown -R cajanus:cajanus /app

# 切换到应用用户
USER cajanus

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV QT_QPA_PLATFORM=offscreen

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, 'src'); from core.config_manager import ConfigManager; print('OK')"

# 启动命令
CMD ["python", "gui_main.py"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  cajanus:
    build: .
    container_name: cajanus-app
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./backups:/app/backups
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
      - CAJANUS_CONFIG_DIR=/app/config
      - CAJANUS_LOG_DIR=/app/logs
    network_mode: host
    privileged: true
    restart: unless-stopped
    
  # 可选：日志收集服务
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logs:/usr/share/logstash/logs:ro
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    depends_on:
      - cajanus
```

### 方式三：预编译包部署

#### 自动化部署脚本
```bash
#!/bin/bash
# deploy_cajanus.sh

set -e

CAJANUS_VERSION="1.0.0"
INSTALL_DIR="/opt/cajanus"
SERVICE_USER="cajanus"

echo "开始部署CAJanus v${CAJANUS_VERSION}..."

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
    PACKAGE_EXT="tar.gz"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="darwin"
    PACKAGE_EXT="tar.gz"
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

# 下载预编译包
PACKAGE_NAME="CAJanus-${CAJANUS_VERSION}-${PLATFORM}-x64.${PACKAGE_EXT}"
DOWNLOAD_URL="https://github.com/your-repo/CAJanus/releases/download/v${CAJANUS_VERSION}/${PACKAGE_NAME}"

echo "下载安装包: $PACKAGE_NAME"
wget -O "/tmp/$PACKAGE_NAME" "$DOWNLOAD_URL"

# 验证校验和
echo "验证文件完整性..."
wget -O "/tmp/checksums.txt" "https://github.com/your-repo/CAJanus/releases/download/v${CAJANUS_VERSION}/checksums.txt"
cd /tmp && sha256sum -c checksums.txt --ignore-missing

# 创建安装目录
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# 解压安装包
echo "解压安装包..."
tar -xzf "/tmp/$PACKAGE_NAME" -C "$INSTALL_DIR" --strip-components=1

# 设置权限
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR/CAJanus"

# 创建符号链接
sudo ln -sf "$INSTALL_DIR/CAJanus" /usr/local/bin/cajanus

echo "部署完成！"
echo "运行 'cajanus' 启动应用程序"
```

---

## 配置管理

### 配置文件结构

#### 生产环境配置
```yaml
# config/production_config.yaml
app:
  name: "CAJanus"
  version: "1.0.0"
  debug: false
  log_level: "INFO"
  
  # 生产环境特定设置
  environment: "production"
  max_concurrent_users: 50
  session_timeout: 3600

# 安全配置
security:
  # 操作确认
  confirmation:
    enable_three_level: true
    require_admin_approval: true
    audit_all_operations: true
  
  # 访问控制
  access_control:
    enable_ip_whitelist: true
    allowed_ips:
      - "192.168.1.0/24"
      - "10.0.0.0/8"
    
    enable_user_authentication: false  # 当前版本不支持
    max_failed_attempts: 3

# 性能配置
performance:
  # 缓存设置
  cache:
    enable_data_cache: true
    cache_expire_seconds: 600
    max_cache_size_mb: 100
  
  # 并发设置
  concurrency:
    enable_parallel_query: true
    max_worker_threads: 8
  
  # 内存管理
  memory:
    max_memory_usage_mb: 1024
    enable_gc_optimization: true
    gc_threshold: 700

# 日志配置
logging:
  level: "INFO"
  
  # 日志文件
  files:
    app_log: "/var/log/cajanus/app.log"
    error_log: "/var/log/cajanus/error.log"
    audit_log: "/var/log/cajanus/audit.log"
    access_log: "/var/log/cajanus/access.log"
  
  # 日志轮转
  rotation:
    max_file_size_mb: 50
    max_file_count: 10
    compress_old_files: true
  
  # 远程日志（可选）
  remote_logging:
    enable: false
    syslog_server: "log.company.com"
    syslog_port: 514

# 备份配置
backup:
  # 自动备份
  auto_backup:
    enable: true
    interval_hours: 24
    max_backup_count: 30
  
  # 备份存储
  storage:
    local_path: "/var/backups/cajanus"
    enable_compression: true
    compression_level: 6
  
  # 远程备份（可选）
  remote_backup:
    enable: false
    type: "s3"  # s3, ftp, sftp
    endpoint: "s3.amazonaws.com"
    bucket: "cajanus-backups"
    access_key: "${AWS_ACCESS_KEY}"
    secret_key: "${AWS_SECRET_KEY}"

# 监控配置
monitoring:
  # 健康检查
  health_check:
    enable: true
    interval_seconds: 60
    endpoint: "/health"
  
  # 性能监控
  performance:
    enable: true
    collect_interval_seconds: 300
    metrics_retention_days: 30
  
  # 告警配置
  alerts:
    enable: true
    email_recipients:
      - "admin@company.com"
    
    thresholds:
      cpu_usage_percent: 80
      memory_usage_percent: 85
      disk_usage_percent: 90
      error_rate_percent: 5
```

### 环境变量配置

#### 系统环境变量
```bash
# /etc/environment 或 ~/.bashrc

# 应用程序配置
export CAJANUS_ENV="production"
export CAJANUS_CONFIG_DIR="/etc/cajanus"
export CAJANUS_LOG_DIR="/var/log/cajanus"
export CAJANUS_BACKUP_DIR="/var/backups/cajanus"
export CAJANUS_DATA_DIR="/var/lib/cajanus"

# 调试和日志
export CAJANUS_DEBUG="false"
export CAJANUS_LOG_LEVEL="INFO"

# 性能调优
export CAJANUS_MAX_MEMORY_MB="1024"
export CAJANUS_MAX_WORKERS="8"

# 安全配置
export CAJANUS_ENABLE_AUDIT="true"
export CAJANUS_REQUIRE_CONFIRMATION="true"

# 数据库配置（如果使用）
export CAJANUS_DB_HOST="localhost"
export CAJANUS_DB_PORT="5432"
export CAJANUS_DB_NAME="cajanus"
export CAJANUS_DB_USER="cajanus_user"
export CAJANUS_DB_PASSWORD="secure_password"

# 外部服务配置
export CAJANUS_SMTP_SERVER="smtp.company.com"
export CAJANUS_SMTP_PORT="587"
export CAJANUS_SMTP_USER="noreply@company.com"
export CAJANUS_SMTP_PASSWORD="smtp_password"
```

### 配置验证

#### 配置验证脚本
```python
#!/usr/bin/env python3
# validate_production_config.py

import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

class ProductionConfigValidator:
    """生产环境配置验证器"""
    
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> bool:
        """验证生产环境配置"""
        if not self.config_file.exists():
            self.errors.append(f"配置文件不存在: {self.config_file}")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"配置文件格式错误: {e}")
            return False
        
        # 验证必需配置
        self._validate_required_config(config)
        
        # 验证安全配置
        self._validate_security_config(config)
        
        # 验证性能配置
        self._validate_performance_config(config)
        
        # 验证日志配置
        self._validate_logging_config(config)
        
        # 验证路径和权限
        self._validate_paths_and_permissions(config)
        
        return len(self.errors) == 0
    
    def _validate_required_config(self, config: Dict[str, Any]):
        """验证必需配置项"""
        required_keys = [
            'app.name',
            'app.version',
            'app.environment',
            'logging.level',
            'security.confirmation.enable_three_level'
        ]
        
        for key in required_keys:
            if not self._get_nested_value(config, key):
                self.errors.append(f"缺少必需配置: {key}")
    
    def _validate_security_config(self, config: Dict[str, Any]):
        """验证安全配置"""
        # 检查是否启用了关键安全功能
        if not self._get_nested_value(config, 'security.confirmation.enable_three_level'):
            self.warnings.append("建议启用三级确认系统")
        
        if not self._get_nested_value(config, 'security.confirmation.audit_all_operations'):
            self.warnings.append("建议启用操作审计")
        
        # 检查访问控制
        if self._get_nested_value(config, 'security.access_control.enable_ip_whitelist'):
            allowed_ips = self._get_nested_value(config, 'security.access_control.allowed_ips')
            if not allowed_ips:
                self.errors.append("启用IP白名单但未配置允许的IP地址")
    
    def _validate_performance_config(self, config: Dict[str, Any]):
        """验证性能配置"""
        max_memory = self._get_nested_value(config, 'performance.memory.max_memory_usage_mb')
        if max_memory and max_memory < 256:
            self.warnings.append(f"内存限制过低: {max_memory}MB，建议至少512MB")
        
        max_workers = self._get_nested_value(config, 'performance.concurrency.max_worker_threads')
        if max_workers and max_workers > 16:
            self.warnings.append(f"工作线程数过多: {max_workers}，可能影响性能")
    
    def _validate_logging_config(self, config: Dict[str, Any]):
        """验证日志配置"""
        log_files = [
            'logging.files.app_log',
            'logging.files.error_log',
            'logging.files.audit_log'
        ]
        
        for log_key in log_files:
            log_path = self._get_nested_value(config, log_key)
            if log_path:
                log_dir = Path(log_path).parent
                if not log_dir.exists():
                    try:
                        log_dir.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        self.errors.append(f"无法创建日志目录 {log_dir}: {e}")
    
    def _validate_paths_and_permissions(self, config: Dict[str, Any]):
        """验证路径和权限"""
        # 检查备份目录
        backup_path = self._get_nested_value(config, 'backup.storage.local_path')
        if backup_path:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                try:
                    backup_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.errors.append(f"无法创建备份目录 {backup_dir}: {e}")
            elif not os.access(backup_dir, os.W_OK):
                self.errors.append(f"备份目录不可写: {backup_dir}")
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """获取嵌套配置值"""
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def print_results(self):
        """打印验证结果"""
        if self.errors:
            print("配置错误:")
            for error in self.errors:
                print(f"  ✗ {error}")
        
        if self.warnings:
            print("配置警告:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        if not self.errors and not self.warnings:
            print("✓ 生产环境配置验证通过")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python validate_production_config.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    validator = ProductionConfigValidator(config_file)
    
    is_valid = validator.validate()
    validator.print_results()
    
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
```

---

## 📚 相关文档

- [配置管理](configuration.md) - 详细的配置参数说明
- [监控运维](monitoring.md) - 监控和维护指南
- [用户指南](../user-guide/installation.md) - 用户安装指南

---

**最后更新**：2024年1月15日  
**适用版本**：v1.0.0+
