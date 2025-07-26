#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义异常类定义
定义系统中使用的各种异常类型
"""

class JanusException(Exception):
    """Janus工具基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

class PermissionError(JanusException):
    """权限相关异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, "PERMISSION_DENIED")

class BackupError(JanusException):
    """备份相关异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "BACKUP_ERROR")

class RestoreError(JanusException):
    """恢复相关异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "RESTORE_ERROR")

class ValidationError(JanusException):
    """验证相关异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class OperationError(JanusException):
    """操作相关异常"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "OPERATION_ERROR")
        self.operation = operation

class PlatformNotSupportedError(JanusException):
    """平台不支持异常"""
    
    def __init__(self, platform: str):
        message = f"平台 {platform} 不受支持"
        super().__init__(message, "PLATFORM_NOT_SUPPORTED")
        self.platform = platform

class ConfigurationError(JanusException):
    """配置相关异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")

class SecurityError(JanusException):
    """安全相关异常"""
    
    def __init__(self, message: str):
        super().__init__(message, "SECURITY_ERROR")

class FileOperationError(JanusException):
    """文件操作异常"""
    
    def __init__(self, message: str, file_path: str = None):
        super().__init__(message, "FILE_OPERATION_ERROR")
        self.file_path = file_path

class NetworkAdapterError(JanusException):
    """网络适配器相关异常"""
    
    def __init__(self, message: str, adapter_id: str = None):
        super().__init__(message, "NETWORK_ADAPTER_ERROR")
        self.adapter_id = adapter_id

class RegistryError(JanusException):
    """注册表操作异常"""
    
    def __init__(self, message: str, registry_path: str = None):
        super().__init__(message, "REGISTRY_ERROR")
        self.registry_path = registry_path
