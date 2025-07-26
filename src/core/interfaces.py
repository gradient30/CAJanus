#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心接口定义
定义系统中各个模块的抽象接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OperationType(Enum):
    """操作类型枚举"""
    READ = "read"
    MODIFY = "modify"
    DELETE = "delete"
    BACKUP = "backup"
    RESTORE = "restore"

class AdapterType(Enum):
    """网卡类型枚举"""
    ETHERNET = "ethernet"
    WIRELESS = "wireless"
    VIRTUAL = "virtual"
    BLUETOOTH = "bluetooth"
    OTHER = "other"

@dataclass
class NetworkAdapter:
    """网络适配器数据结构"""
    id: str
    name: str
    description: str
    mac_address: str
    status: str
    adapter_type: AdapterType
    can_modify: bool
    registry_path: Optional[str] = None  # Windows专用
    interface_name: Optional[str] = None  # macOS专用

@dataclass
class BackupItem:
    """备份项目数据结构"""
    item_type: str  # 'registry', 'file', 'config'
    source_path: str
    backup_path: str
    size: int
    checksum: str

@dataclass
class BackupInfo:
    """备份信息数据结构"""
    backup_id: str
    timestamp: datetime
    backup_type: str  # 'full', 'incremental', 'selective'
    items: List[BackupItem]
    total_size: int
    description: str
    platform: str

@dataclass
class OperationRecord:
    """操作记录数据结构"""
    operation_id: str
    timestamp: datetime
    operation_type: OperationType
    target: str
    parameters: Dict[str, Any]
    result: str
    backup_id: Optional[str]
    risk_level: RiskLevel
    user: str
    duration: float

@dataclass
class ValidationResult:
    """验证结果数据结构"""
    is_valid: bool
    risk_level: RiskLevel
    errors: List[str]
    warnings: List[str]
    required_permissions: List[str]

    def __init__(self):
        self.is_valid = True
        self.risk_level = RiskLevel.LOW
        self.errors = []
        self.warnings = []
        self.required_permissions = []

    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """添加警告信息"""
        self.warnings.append(warning)

@dataclass
class ProcessInfo:
    """进程信息数据结构"""
    pid: int
    name: str
    exe_path: str
    command_line: str
    user: str

class IDeviceFingerprintManager(ABC):
    """设备指纹管理器接口"""
    
    @abstractmethod
    def get_network_adapters(self) -> List[NetworkAdapter]:
        """获取所有网络适配器信息"""
        pass
    
    @abstractmethod
    def get_mac_address(self, adapter_id: str) -> Optional[str]:
        """获取指定网卡的MAC地址"""
        pass
    
    @abstractmethod
    def modify_mac_address(self, adapter_id: str, new_mac: str) -> bool:
        """修改指定网卡的MAC地址"""
        pass
    
    @abstractmethod
    def get_machine_guid(self) -> Optional[str]:
        """获取机器GUID"""
        pass
    
    @abstractmethod
    def modify_machine_guid(self, new_guid: str) -> bool:
        """修改机器GUID"""
        pass
    
    @abstractmethod
    def get_volume_serial_numbers(self) -> Dict[str, str]:
        """获取磁盘卷序列号"""
        pass
    
    @abstractmethod
    def modify_volume_serial(self, drive: str, new_serial: str) -> bool:
        """修改磁盘卷序列号"""
        pass
    
    @abstractmethod
    def get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        pass

class IBackupManager(ABC):
    """备份管理器接口"""
    
    @abstractmethod
    def create_backup(self, items: List[str], backup_type: str = "selective") -> str:
        """创建备份"""
        pass
    
    @abstractmethod
    def restore_backup(self, backup_id: str, items: Optional[List[str]] = None) -> bool:
        """恢复备份"""
        pass
    
    @abstractmethod
    def list_backups(self) -> List[BackupInfo]:
        """列出所有备份"""
        pass
    
    @abstractmethod
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        pass
    
    @abstractmethod
    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """获取备份详细信息"""
        pass

class ISecurityValidator(ABC):
    """安全验证器接口"""
    
    @abstractmethod
    def validate_operation(self, operation_type: OperationType, 
                         target: str, parameters: Dict[str, Any]) -> ValidationResult:
        """验证操作的安全性"""
        pass
    
    @abstractmethod
    def check_permissions(self, required_permissions: List[str]) -> bool:
        """检查权限"""
        pass
    
    @abstractmethod
    def assess_risk(self, operation_type: OperationType, target: str) -> RiskLevel:
        """评估操作风险等级"""
        pass

class IPermissionManager(ABC):
    """权限管理器接口"""
    
    @abstractmethod
    def check_admin_privileges(self) -> bool:
        """检查管理员权限"""
        pass
    
    @abstractmethod
    def request_elevation(self) -> bool:
        """请求权限提升"""
        pass
    
    @abstractmethod
    def get_current_user(self) -> str:
        """获取当前用户"""
        pass

class IFileOperationManager(ABC):
    """文件操作管理器接口"""
    
    @abstractmethod
    def safe_delete(self, path: Path, create_backup: bool = True) -> bool:
        """安全删除文件或文件夹"""
        pass
    
    @abstractmethod
    def restore_from_backup(self, backup_id: str, target_path: Path) -> bool:
        """从备份恢复文件"""
        pass
    
    @abstractmethod
    def check_file_usage(self, file_path: Path) -> List[ProcessInfo]:
        """检查文件被哪些进程占用"""
        pass
    
    @abstractmethod
    def scan_application_data(self, app_name: str) -> List[Path]:
        """扫描应用程序数据目录"""
        pass

class IAuditLogger(ABC):
    """审计日志记录器接口"""
    
    @abstractmethod
    def log_operation(self, record: OperationRecord):
        """记录操作日志"""
        pass
    
    @abstractmethod
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """记录安全事件"""
        pass
    
    @abstractmethod
    def get_operation_history(self, limit: int = 100) -> List[OperationRecord]:
        """获取操作历史"""
        pass
    
    @abstractmethod
    def search_logs(self, query: str, start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[OperationRecord]:
        """搜索日志"""
        pass

class IConfigManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any):
        """设置配置值"""
        pass
    
    @abstractmethod
    def save_config(self):
        """保存配置到文件"""
        pass
    
    @abstractmethod
    def load_config(self):
        """从文件加载配置"""
        pass

class IEducationHelper(ABC):
    """教育辅助功能接口"""
    
    @abstractmethod
    def get_principle_explanation(self, topic: str) -> str:
        """获取原理解释"""
        pass
    
    @abstractmethod
    def get_operation_guide(self, operation: str) -> List[str]:
        """获取操作指导"""
        pass
    
    @abstractmethod
    def get_risk_explanation(self, risk_level: RiskLevel) -> str:
        """获取风险说明"""
        pass
    
    @abstractmethod
    def suggest_learning_resources(self, topic: str) -> List[str]:
        """推荐学习资源"""
        pass
