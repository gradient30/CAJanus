#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统实现
提供统一的日志记录功能，包括操作审计和系统日志
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import threading
from .interfaces import IAuditLogger, OperationRecord
from .config_manager import get_config_manager
from .exceptions import ConfigurationError

class JanusLogger:
    """Janus工具日志记录器"""
    
    def __init__(self, name: str = "janus"):
        self.name = name
        self.config_manager = get_config_manager()
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        try:
            # 清除现有的处理器
            self.logger.handlers.clear()
            
            # 设置日志级别
            log_level = self.config_manager.get_config('app.log_level', 'INFO')
            self.logger.setLevel(getattr(logging, log_level.upper()))
            
            # 获取日志目录
            log_dir = self.config_manager.get_log_directory()
            
            # 设置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # 文件处理器 - 应用日志
            app_log_file = log_dir / f"{self.name}.log"
            max_log_size = self.config_manager.get_config('logging.max_log_size', 10485760)
            max_log_files = self.config_manager.get_config('logging.max_log_files', 5)
            
            file_handler = logging.handlers.RotatingFileHandler(
                app_log_file, maxBytes=max_log_size, backupCount=max_log_files,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # 控制台处理器（调试模式下）
            if self.config_manager.is_debug_mode():
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
                
        except Exception as e:
            raise ConfigurationError(f"设置日志记录器失败: {e}")
    
    def debug(self, message: str, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """记录信息"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误"""
        self.logger.critical(message, extra=kwargs)

class AuditLogger(IAuditLogger):
    """审计日志记录器"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.audit_file = self.config_manager.get_log_directory() / "audit.log"
        self.lock = threading.Lock()
        self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """设置审计日志记录器"""
        try:
            self.audit_logger = logging.getLogger("audit")
            self.audit_logger.setLevel(logging.INFO)
            
            # 清除现有处理器
            self.audit_logger.handlers.clear()
            
            # 审计日志文件处理器
            max_log_size = self.config_manager.get_config('logging.max_log_size', 10485760)
            max_log_files = self.config_manager.get_config('logging.max_log_files', 5)
            
            audit_handler = logging.handlers.RotatingFileHandler(
                self.audit_file, maxBytes=max_log_size, backupCount=max_log_files,
                encoding='utf-8'
            )
            
            # 审计日志使用JSON格式
            audit_formatter = logging.Formatter('%(message)s')
            audit_handler.setFormatter(audit_formatter)
            self.audit_logger.addHandler(audit_handler)
            
        except Exception as e:
            raise ConfigurationError(f"设置审计日志记录器失败: {e}")
    
    def log_operation(self, record: OperationRecord):
        """记录操作日志"""
        if not self.config_manager.get_config('security.enable_audit_log', True):
            return
        
        try:
            with self.lock:
                audit_data = {
                    'operation_id': record.operation_id,
                    'timestamp': record.timestamp.isoformat(),
                    'operation_type': record.operation_type.value,
                    'target': record.target,
                    'parameters': record.parameters,
                    'result': record.result,
                    'backup_id': record.backup_id,
                    'risk_level': record.risk_level.value,
                    'user': record.user,
                    'duration': record.duration
                }
                
                self.audit_logger.info(json.dumps(audit_data, ensure_ascii=False))
                
        except Exception as e:
            # 审计日志失败不应该影响主要功能
            logger = JanusLogger("audit_error")
            logger.error(f"记录审计日志失败: {e}")
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """记录安全事件"""
        if not self.config_manager.get_config('security.enable_audit_log', True):
            return
        
        try:
            with self.lock:
                security_data = {
                    'event_type': 'security_event',
                    'security_event_type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'details': details
                }
                
                self.audit_logger.info(json.dumps(security_data, ensure_ascii=False))
                
        except Exception as e:
            logger = JanusLogger("audit_error")
            logger.error(f"记录安全事件失败: {e}")
    
    def get_operation_history(self, limit: int = 100) -> List[OperationRecord]:
        """获取操作历史"""
        try:
            records = []
            
            if not self.audit_file.exists():
                return records
            
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 从最新的记录开始读取
            for line in reversed(lines[-limit:]):
                try:
                    data = json.loads(line.strip())
                    
                    # 只处理操作记录，跳过安全事件
                    if data.get('event_type') == 'security_event':
                        continue
                    
                    record = OperationRecord(
                        operation_id=data['operation_id'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        operation_type=data['operation_type'],
                        target=data['target'],
                        parameters=data['parameters'],
                        result=data['result'],
                        backup_id=data.get('backup_id'),
                        risk_level=data['risk_level'],
                        user=data['user'],
                        duration=data['duration']
                    )
                    records.append(record)
                    
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return records
            
        except Exception as e:
            logger = JanusLogger("audit_error")
            logger.error(f"获取操作历史失败: {e}")
            return []
    
    def search_logs(self, query: str, start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[OperationRecord]:
        """搜索日志"""
        try:
            records = []
            
            if not self.audit_file.exists():
                return records
            
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        
                        # 跳过安全事件
                        if data.get('event_type') == 'security_event':
                            continue
                        
                        # 时间过滤
                        record_time = datetime.fromisoformat(data['timestamp'])
                        if start_time and record_time < start_time:
                            continue
                        if end_time and record_time > end_time:
                            continue
                        
                        # 内容搜索
                        if query.lower() in json.dumps(data, ensure_ascii=False).lower():
                            record = OperationRecord(
                                operation_id=data['operation_id'],
                                timestamp=record_time,
                                operation_type=data['operation_type'],
                                target=data['target'],
                                parameters=data['parameters'],
                                result=data['result'],
                                backup_id=data.get('backup_id'),
                                risk_level=data['risk_level'],
                                user=data['user'],
                                duration=data['duration']
                            )
                            records.append(record)
                            
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return records
            
        except Exception as e:
            logger = JanusLogger("audit_error")
            logger.error(f"搜索日志失败: {e}")
            return []
    
    def cleanup_old_logs(self):
        """清理过期日志"""
        try:
            retention_days = self.config_manager.get_config('logging.log_retention_days', 30)
            if retention_days <= 0:
                return
            
            cutoff_time = datetime.now().timestamp() - (retention_days * 24 * 3600)
            
            if not self.audit_file.exists():
                return
            
            # 读取所有日志
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤保留的日志
            kept_lines = []
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    record_time = datetime.fromisoformat(data['timestamp']).timestamp()
                    if record_time >= cutoff_time:
                        kept_lines.append(line)
                except (json.JSONDecodeError, KeyError):
                    # 保留无法解析的行
                    kept_lines.append(line)
            
            # 写回文件
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                f.writelines(kept_lines)
                
        except Exception as e:
            logger = JanusLogger("audit_error")
            logger.error(f"清理过期日志失败: {e}")

# 全局日志实例
_main_logger: Optional[JanusLogger] = None
_audit_logger: Optional[AuditLogger] = None

def get_logger(name: str = "janus") -> JanusLogger:
    """获取日志记录器实例"""
    global _main_logger
    if _main_logger is None or _main_logger.name != name:
        _main_logger = JanusLogger(name)
    return _main_logger

def get_audit_logger() -> AuditLogger:
    """获取审计日志记录器实例"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
