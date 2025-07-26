# API 参考文档

> 📚 **接口文档和示例** - CAJanus核心API的详细说明和使用示例

## 📋 目录

1. [API概览](#API概览)
2. [核心接口](#核心接口)
3. [平台接口](#平台接口)
4. [数据模型](#数据模型)
5. [错误处理](#错误处理)
6. [使用示例](#使用示例)

---

## API概览

### 设计原则
- **统一接口**：所有平台使用相同的API接口
- **类型安全**：完整的类型提示和验证
- **异步支持**：支持同步和异步调用
- **错误处理**：统一的错误处理机制

### 核心模块
```python
from src.core.config_manager import ConfigManager
from src.core.platform_factory import PlatformFactory
from src.core.i18n_manager import I18nManager
from src.platforms.base import IFingerprintEngine
from src.ui.main_window import MainWindow
```

---

## 核心接口

### ConfigManager - 配置管理

#### 类定义
```python
class ConfigManager:
    """配置管理器 - 统一的配置管理接口"""
    
    def __init__(self, config_file: str = "config/user_config.yaml"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
```

#### 主要方法

##### get_config()
```python
def get_config(self, key: str, default: Any = None) -> Any:
    """获取配置值
    
    Args:
        key: 配置键，支持点号分隔的嵌套键 (如 'ui.theme')
        default: 默认值
        
    Returns:
        配置值或默认值
        
    Example:
        >>> config = ConfigManager()
        >>> theme = config.get_config('ui.theme', 'default')
        >>> print(theme)
        'default'
    """
```

##### set_config()
```python
def set_config(self, key: str, value: Any) -> None:
    """设置配置值
    
    Args:
        key: 配置键
        value: 配置值
        
    Raises:
        ValueError: 当键格式无效时
        
    Example:
        >>> config = ConfigManager()
        >>> config.set_config('ui.theme', 'dark')
        >>> config.save_config()
    """
```

##### watch_config()
```python
def watch_config(self, key: str, callback: Callable[[str, Any], None]) -> None:
    """监听配置变更
    
    Args:
        key: 要监听的配置键
        callback: 变更回调函数
        
    Example:
        >>> def on_theme_change(key, value):
        ...     print(f"主题变更为: {value}")
        >>> config.watch_config('ui.theme', on_theme_change)
    """
```

### PlatformFactory - 平台工厂

#### 类定义
```python
class PlatformFactory:
    """平台工厂 - 创建平台特定的实现"""
    
    @classmethod
    def get_fingerprint_engine(cls) -> IFingerprintEngine:
        """获取当前平台的指纹识别引擎
        
        Returns:
            当前平台的指纹识别引擎实例
            
        Raises:
            UnsupportedPlatformError: 当平台不支持时
            
        Example:
            >>> engine = PlatformFactory.get_fingerprint_engine()
            >>> adapters = engine.get_network_adapters()
        """
```

### I18nManager - 国际化管理

#### 类定义
```python
class I18nManager:
    """国际化管理器"""
    
    def __init__(self, language: str = "zh_CN"):
        """初始化国际化管理器
        
        Args:
            language: 语言代码 (zh_CN, en_US, zh_TW, ja_JP)
        """
```

#### 主要方法

##### get_text()
```python
def get_text(self, key: str, **kwargs) -> str:
    """获取翻译文本
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
        
    Example:
        >>> i18n = I18nManager('en_US')
        >>> text = i18n.get_text('app.name')
        >>> print(text)
        'CAJanus'
        
        >>> text = i18n.get_text('status.connected', count=5)
        >>> print(text)
        '5 adapters connected'
    """
```

---

## 平台接口

### IFingerprintEngine - 指纹识别引擎接口

#### 接口定义
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class IFingerprintEngine(ABC):
    """设备指纹识别引擎接口"""
    
    @abstractmethod
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """获取网络适配器列表
        
        Returns:
            网络适配器列表
            
        Raises:
            PermissionError: 权限不足时
            SystemError: 系统错误时
        """
        pass
    
    @abstractmethod
    def get_system_info(self) -> SystemInfo:
        """获取系统信息
        
        Returns:
            系统信息对象
        """
        pass
    
    @abstractmethod
    def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
        """修改MAC地址
        
        Args:
            adapter_id: 适配器ID
            new_mac: 新MAC地址 (格式: XX:XX:XX:XX:XX:XX)
            
        Returns:
            修改是否成功
            
        Raises:
            ValueError: MAC地址格式无效
            PermissionError: 权限不足
            AdapterNotFoundError: 适配器不存在
        """
        pass
```

### 平台特定实现

#### WindowsFingerprintEngine
```python
class WindowsFingerprintEngine(IFingerprintEngine):
    """Windows平台指纹识别引擎"""
    
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """获取Windows网络适配器
        
        使用WMI查询网络适配器信息
        
        Returns:
            网络适配器列表
        """
        
    def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
        """修改Windows网络适配器MAC地址
        
        通过注册表修改MAC地址
        
        Args:
            adapter_id: 适配器注册表键
            new_mac: 新MAC地址
            
        Returns:
            修改是否成功
        """
```

---

## 数据模型

### NetworkAdapter - 网络适配器

```python
@dataclass
class NetworkAdapter:
    """网络适配器数据模型"""
    
    id: str                    # 适配器唯一标识
    name: str                  # 适配器名称
    description: str           # 适配器描述
    mac_address: str          # MAC地址 (格式: XX:XX:XX:XX:XX:XX)
    ip_addresses: List[str]   # IP地址列表
    status: AdapterStatus     # 适配器状态
    adapter_type: AdapterType # 适配器类型
    is_physical: bool         # 是否为物理适配器
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkAdapter':
        """从字典创建实例"""
        return cls(**data)
```

### SystemInfo - 系统信息

```python
@dataclass
class SystemInfo:
    """系统信息数据模型"""
    
    os_name: str              # 操作系统名称
    os_version: str           # 操作系统版本
    architecture: str         # 系统架构
    hostname: str             # 主机名
    username: str             # 当前用户名
    boot_time: datetime       # 启动时间
    cpu_info: CPUInfo         # CPU信息
    memory_info: MemoryInfo   # 内存信息
    disk_info: List[DiskInfo] # 磁盘信息
    
    @property
    def uptime(self) -> timedelta:
        """系统运行时间"""
        return datetime.now() - self.boot_time
```

### 枚举类型

```python
class AdapterStatus(Enum):
    """适配器状态枚举"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DISABLED = "disabled"
    UNKNOWN = "unknown"

class AdapterType(Enum):
    """适配器类型枚举"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    VIRTUAL = "virtual"
    LOOPBACK = "loopback"
    OTHER = "other"

class PlatformType(Enum):
    """平台类型枚举"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
```

---

## 错误处理

### 异常类层次结构

```python
class CAJanusError(Exception):
    """CAJanus基础异常类"""
    pass

class ConfigError(CAJanusError):
    """配置相关错误"""
    pass

class PlatformError(CAJanusError):
    """平台相关错误"""
    pass

class UnsupportedPlatformError(PlatformError):
    """不支持的平台错误"""
    pass

class AdapterError(CAJanusError):
    """适配器相关错误"""
    pass

class AdapterNotFoundError(AdapterError):
    """适配器未找到错误"""
    pass

class ValidationError(CAJanusError):
    """数据验证错误"""
    pass

class PermissionError(CAJanusError):
    """权限错误"""
    pass
```

### 错误处理示例

```python
try:
    engine = PlatformFactory.get_fingerprint_engine()
    adapters = engine.get_network_adapters()
except UnsupportedPlatformError as e:
    logger.error(f"不支持的平台: {e}")
    # 处理不支持的平台
except PermissionError as e:
    logger.error(f"权限不足: {e}")
    # 提示用户获取权限
except CAJanusError as e:
    logger.error(f"CAJanus错误: {e}")
    # 通用错误处理
except Exception as e:
    logger.error(f"未知错误: {e}")
    # 未知错误处理
```

---

## 使用示例

### 基础使用示例

#### 获取网络适配器信息
```python
from src.core.platform_factory import PlatformFactory

def get_adapter_info():
    """获取网络适配器信息示例"""
    try:
        # 获取平台引擎
        engine = PlatformFactory.get_fingerprint_engine()
        
        # 获取网络适配器列表
        adapters = engine.get_network_adapters()
        
        # 打印适配器信息
        for adapter in adapters:
            print(f"适配器: {adapter.name}")
            print(f"MAC地址: {adapter.mac_address}")
            print(f"状态: {adapter.status.value}")
            print(f"类型: {adapter.adapter_type.value}")
            print("-" * 40)
            
    except Exception as e:
        print(f"获取适配器信息失败: {e}")

# 调用示例
get_adapter_info()
```

#### 修改MAC地址
```python
async def modify_mac_example():
    """修改MAC地址示例"""
    try:
        engine = PlatformFactory.get_fingerprint_engine()
        
        # 获取第一个物理适配器
        adapters = engine.get_network_adapters()
        physical_adapters = [a for a in adapters if a.is_physical]
        
        if not physical_adapters:
            print("未找到物理网络适配器")
            return
        
        adapter = physical_adapters[0]
        new_mac = "00:11:22:33:44:55"
        
        print(f"准备修改适配器 {adapter.name} 的MAC地址")
        print(f"当前MAC: {adapter.mac_address}")
        print(f"新MAC: {new_mac}")
        
        # 执行修改
        success = engine.modify_mac_address(adapter.id, new_mac)
        
        if success:
            print("MAC地址修改成功")
        else:
            print("MAC地址修改失败")
            
    except Exception as e:
        print(f"修改MAC地址失败: {e}")

# 异步调用示例
import asyncio
asyncio.run(modify_mac_example())
```

#### 配置管理示例
```python
from src.core.config_manager import ConfigManager

def config_example():
    """配置管理示例"""
    config = ConfigManager()
    
    # 获取配置
    theme = config.get_config('ui.theme', 'default')
    language = config.get_config('ui.language', 'zh_CN')
    
    print(f"当前主题: {theme}")
    print(f"当前语言: {language}")
    
    # 设置配置
    config.set_config('ui.theme', 'dark')
    config.set_config('ui.font_size', 12)
    
    # 监听配置变更
    def on_theme_change(key, value):
        print(f"主题已变更为: {value}")
    
    config.watch_config('ui.theme', on_theme_change)
    
    # 保存配置
    config.save_config()

config_example()
```

### 高级使用示例

#### 自定义平台引擎
```python
from src.platforms.base import IFingerprintEngine
from src.core.platform_factory import PlatformFactory

class CustomFingerprintEngine(IFingerprintEngine):
    """自定义指纹识别引擎"""
    
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """自定义网络适配器获取逻辑"""
        # 实现自定义逻辑
        pass
    
    def get_system_info(self) -> SystemInfo:
        """自定义系统信息获取逻辑"""
        # 实现自定义逻辑
        pass
    
    def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
        """自定义MAC地址修改逻辑"""
        # 实现自定义逻辑
        pass

# 注册自定义引擎
PlatformFactory.register_engine(PlatformType.CUSTOM, CustomFingerprintEngine)
```

#### 插件开发示例
```python
from src.core.plugin_manager import Plugin

class ExamplePlugin(Plugin):
    """示例插件"""
    
    def get_name(self) -> str:
        return "示例插件"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def initialize(self, context):
        """插件初始化"""
        self.context = context
        print("示例插件已初始化")
    
    def get_hooks(self) -> Dict[str, Callable]:
        """获取插件钩子"""
        return {
            'before_modify_mac': self.before_modify_mac,
            'after_modify_mac': self.after_modify_mac
        }
    
    def before_modify_mac(self, adapter_id: str, new_mac: str):
        """MAC地址修改前钩子"""
        print(f"准备修改MAC地址: {adapter_id} -> {new_mac}")
    
    def after_modify_mac(self, adapter_id: str, new_mac: str, success: bool):
        """MAC地址修改后钩子"""
        status = "成功" if success else "失败"
        print(f"MAC地址修改{status}: {adapter_id} -> {new_mac}")

# 注册插件
plugin_manager = PluginManager()
plugin_manager.register_plugin(ExamplePlugin())
```

---

## 📚 相关文档

- [开发指南](development-guide.md) - 开发环境和流程
- [架构设计](architecture.md) - 系统架构和设计原理
- [用户手册](../user-guide/user-manual.md) - 用户功能说明

---

**最后更新**：2024年1月15日  
**API版本**：v1.0.0
