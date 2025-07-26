#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器实现
负责应用程序配置的加载、保存和管理
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging
from .interfaces import IConfigManager
from .exceptions import ConfigurationError

class ConfigManager(IConfigManager):
    """配置管理器实现"""
    
    def __init__(self, config_file: str = "config/user_config.yaml"):
        self.logger = logging.getLogger("config_manager")
        self.config_file = Path(config_file)
        self.default_config_file = Path("config/default_config.yaml")
        self.config: Dict[str, Any] = {}
        self._load_default_config()
        self.load_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        try:
            if self.default_config_file.exists():
                with open(self.default_config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                # 如果默认配置文件不存在，使用硬编码的默认配置
                self.config = self._get_hardcoded_defaults()
        except Exception as e:
            raise ConfigurationError(f"加载默认配置失败: {e}")
    
    def _get_hardcoded_defaults(self) -> Dict[str, Any]:
        """获取硬编码的默认配置"""
        return {
            'app': {
                'name': '设备指纹识别与修改工具',
                'version': '1.0.0-alpha',
                'debug': False,
                'log_level': 'INFO'
            },
            'ui': {
                'theme': 'default',
                'language': 'zh_CN',
                'window_size': {'width': 1200, 'height': 800},
                'show_warnings': True
            },
            'security': {
                'require_confirmation': True,
                'backup_before_modify': True,
                'max_backup_count': 10,
                'enable_audit_log': True
            },
            'education': {
                'show_principles': True,
                'detailed_logs': True,
                'learning_mode': False
            },
            'backup': {
                'backup_directory': './backups',
                'compression_enabled': True,
                'max_backup_size': 1073741824  # 1GB
            },
            'logging': {
                'log_directory': './logs',
                'max_log_size': 10485760,  # 10MB
                'max_log_files': 5
            }
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'ui.theme'
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set_config(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # 导航到目标位置
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
        except Exception as e:
            raise ConfigurationError(f"设置配置失败: {e}")
    
    def load_config(self):
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    # 合并用户配置到默认配置
                    self._merge_config(self.config, user_config)
        except Exception as e:
            raise ConfigurationError(f"加载用户配置失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            raise ConfigurationError(f"保存配置失败: {e}")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """递归合并配置字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_backup_directory(self) -> Path:
        """获取备份目录路径"""
        backup_dir = Path(self.get_config('backup.backup_directory', './backups'))
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def get_log_directory(self) -> Path:
        """获取日志目录路径"""
        log_dir = Path(self.get_config('logging.log_directory', './logs'))
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def is_debug_mode(self) -> bool:
        """检查是否为调试模式"""
        return self.get_config('app.debug', False)
    
    def is_learning_mode(self) -> bool:
        """检查是否为学习模式"""
        return self.get_config('education.learning_mode', False)
    
    def get_ui_language(self) -> str:
        """获取界面语言"""
        return self.get_config('ui.language', 'zh_CN')
    
    def get_window_size(self) -> tuple:
        """获取窗口大小"""
        size = self.get_config('ui.window_size', {'width': 1200, 'height': 800})
        return (size.get('width', 1200), size.get('height', 800))
    
    def should_backup_before_modify(self) -> bool:
        """检查是否在修改前备份"""
        return self.get_config('security.backup_before_modify', True)
    
    def should_require_confirmation(self) -> bool:
        """检查是否需要确认"""
        return self.get_config('security.require_confirmation', True)
    
    def get_max_backup_count(self) -> int:
        """获取最大备份数量"""
        return self.get_config('security.max_backup_count', 10)
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self._load_default_config()
        self.save_config()
    
    def export_config(self, export_path: str):
        """导出配置到指定文件"""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            # 根据文件扩展名选择格式
            if export_path.lower().endswith('.json'):
                import json
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            else:
                # 默认使用YAML格式
                with open(export_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False,
                             allow_unicode=True, indent=2)
        except Exception as e:
            raise ConfigurationError(f"导出配置失败: {e}")
    
    def import_config(self, import_path: str):
        """从指定文件导入配置"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise ConfigurationError(f"配置文件不存在: {import_path}")

            # 根据文件扩展名选择解析格式
            with open(import_file, 'r', encoding='utf-8') as f:
                if import_path.lower().endswith('.json'):
                    import json
                    imported_config = json.load(f) or {}
                else:
                    # 默认使用YAML格式
                    imported_config = yaml.safe_load(f) or {}

                self._merge_config(self.config, imported_config)
                self.save_config()
        except Exception as e:
            raise ConfigurationError(f"导入配置失败: {e}")
    
    def load_from_file(self, file_path: str) -> bool:
        """从文件加载配置"""
        try:
            self.import_config(file_path)
            return True
        except Exception as e:
            self.logger.error(f"从文件加载配置失败: {e}")
            return False

    def save_to_file(self, file_path: str) -> bool:
        """保存配置到文件"""
        try:
            # 检查路径是否有效
            test_path = Path(file_path)
            if not test_path.parent.exists():
                # 尝试创建父目录
                try:
                    test_path.parent.mkdir(parents=True, exist_ok=True)
                except (OSError, PermissionError):
                    self.logger.error(f"无法创建目录: {test_path.parent}")
                    return False

            self.export_config(file_path)
            return True
        except Exception as e:
            self.logger.error(f"保存配置到文件失败: {e}")
            return False

    def validate_config(self) -> bool:
        """验证配置的有效性"""
        try:
            # 检查必要的配置项
            required_keys = [
                'app.name',
                'app.version',
                'backup.backup_directory',
                'logging.log_directory'
            ]

            for key in required_keys:
                if self.get_config(key) is None:
                    raise ConfigurationError(f"缺少必要的配置项: {key}")

            # 检查目录权限
            backup_dir = self.get_backup_directory()
            log_dir = self.get_log_directory()

            if not os.access(backup_dir.parent, os.W_OK):
                raise ConfigurationError(f"备份目录无写入权限: {backup_dir}")

            if not os.access(log_dir.parent, os.W_OK):
                raise ConfigurationError(f"日志目录无写入权限: {log_dir}")

            return True

        except Exception as e:
            raise ConfigurationError(f"配置验证失败: {e}")

# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
