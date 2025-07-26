#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows注册表管理器
提供安全的注册表操作功能，包括备份、修改和恢复
"""

import winreg
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.logger import get_logger
from core.config_manager import get_config_manager
from core.exceptions import RegistryError, BackupError

class RegistryManager:
    """Windows注册表管理器"""
    
    def __init__(self):
        self.logger = get_logger("registry_manager")
        self.config_manager = get_config_manager()
        self.backup_dir = self.config_manager.get_backup_directory() / "registry"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 注册表根键映射
        self.root_keys = {
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
            'HKEY_USERS': winreg.HKEY_USERS,
            'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
        }
        
        self.logger.info("注册表管理器初始化完成")
    
    def _parse_registry_path(self, registry_path: str) -> Tuple[int, str]:
        """解析注册表路径"""
        for root_name, root_key in self.root_keys.items():
            if registry_path.startswith(root_name):
                sub_path = registry_path[len(root_name):].lstrip('\\')
                return root_key, sub_path
        
        raise RegistryError(f"无效的注册表路径: {registry_path}")
    
    def read_value(self, registry_path: str, value_name: str) -> Optional[Any]:
        """读取注册表值"""
        try:
            root_key, sub_path = self._parse_registry_path(registry_path)
            
            with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_READ) as key:
                value, reg_type = winreg.QueryValueEx(key, value_name)
                
                self.logger.debug(f"读取注册表值: {registry_path}\\{value_name} = {value}")
                return value
                
        except FileNotFoundError:
            self.logger.warning(f"注册表键或值不存在: {registry_path}\\{value_name}")
            return None
        except PermissionError:
            self.logger.error(f"注册表访问权限不足: {registry_path}")
            raise RegistryError(f"注册表访问权限不足: {registry_path}")
        except Exception as e:
            self.logger.error(f"读取注册表值失败: {e}")
            raise RegistryError(f"读取注册表值失败: {e}")
    
    def write_value(self, registry_path: str, value_name: str, value: Any, 
                   reg_type: int = winreg.REG_SZ, create_backup: bool = True) -> bool:
        """写入注册表值"""
        try:
            # 创建备份
            if create_backup:
                backup_id = self.backup_registry_key(registry_path)
                self.logger.info(f"注册表备份ID: {backup_id}")
            
            root_key, sub_path = self._parse_registry_path(registry_path)
            
            with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, value_name, 0, reg_type, value)
                
                self.logger.info(f"写入注册表值: {registry_path}\\{value_name} = {value}")
                return True
                
        except PermissionError:
            self.logger.error(f"注册表写入权限不足: {registry_path}")
            raise RegistryError(f"注册表写入权限不足: {registry_path}")
        except Exception as e:
            self.logger.error(f"写入注册表值失败: {e}")
            raise RegistryError(f"写入注册表值失败: {e}")
    
    def delete_value(self, registry_path: str, value_name: str, 
                    create_backup: bool = True) -> bool:
        """删除注册表值"""
        try:
            # 创建备份
            if create_backup:
                backup_id = self.backup_registry_key(registry_path)
                self.logger.info(f"注册表备份ID: {backup_id}")
            
            root_key, sub_path = self._parse_registry_path(registry_path)
            
            with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, value_name)
                
                self.logger.info(f"删除注册表值: {registry_path}\\{value_name}")
                return True
                
        except FileNotFoundError:
            self.logger.warning(f"注册表值不存在: {registry_path}\\{value_name}")
            return False
        except PermissionError:
            self.logger.error(f"注册表删除权限不足: {registry_path}")
            raise RegistryError(f"注册表删除权限不足: {registry_path}")
        except Exception as e:
            self.logger.error(f"删除注册表值失败: {e}")
            raise RegistryError(f"删除注册表值失败: {e}")
    
    def enumerate_values(self, registry_path: str) -> List[Dict[str, Any]]:
        """枚举注册表键下的所有值"""
        try:
            root_key, sub_path = self._parse_registry_path(registry_path)
            values = []
            
            with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        value_name, value_data, reg_type = winreg.EnumValue(key, i)
                        values.append({
                            'name': value_name,
                            'data': value_data,
                            'type': reg_type
                        })
                        i += 1
                    except OSError:
                        break
            
            self.logger.debug(f"枚举注册表值: {registry_path}, 找到 {len(values)} 个值")
            return values
            
        except FileNotFoundError:
            self.logger.warning(f"注册表键不存在: {registry_path}")
            return []
        except PermissionError:
            self.logger.error(f"注册表访问权限不足: {registry_path}")
            raise RegistryError(f"注册表访问权限不足: {registry_path}")
        except Exception as e:
            self.logger.error(f"枚举注册表值失败: {e}")
            raise RegistryError(f"枚举注册表值失败: {e}")
    
    def backup_registry_key(self, registry_path: str) -> str:
        """备份注册表键"""
        try:
            backup_id = f"registry_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            backup_file = self.backup_dir / f"{backup_id}.json"
            
            # 读取注册表键的所有值
            values = self.enumerate_values(registry_path)
            
            backup_data = {
                'backup_id': backup_id,
                'timestamp': datetime.now().isoformat(),
                'registry_path': registry_path,
                'values': values
            }
            
            # 保存备份文件
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"注册表备份完成: {backup_id}, 文件: {backup_file}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"注册表备份失败: {e}")
            raise BackupError(f"注册表备份失败: {e}")
    
    def restore_registry_backup(self, backup_id: str) -> bool:
        """恢复注册表备份"""
        try:
            backup_file = self.backup_dir / f"{backup_id}.json"
            
            if not backup_file.exists():
                raise BackupError(f"备份文件不存在: {backup_id}")
            
            # 读取备份数据
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            registry_path = backup_data['registry_path']
            values = backup_data['values']
            
            # 恢复注册表值
            for value_info in values:
                self.write_value(
                    registry_path,
                    value_info['name'],
                    value_info['data'],
                    value_info['type'],
                    create_backup=False  # 恢复时不创建备份
                )
            
            self.logger.info(f"注册表恢复完成: {backup_id}, 恢复了 {len(values)} 个值")
            return True
            
        except Exception as e:
            self.logger.error(f"注册表恢复失败: {e}")
            raise BackupError(f"注册表恢复失败: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有注册表备份"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.json"):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    backups.append({
                        'backup_id': backup_data['backup_id'],
                        'timestamp': backup_data['timestamp'],
                        'registry_path': backup_data['registry_path'],
                        'value_count': len(backup_data['values']),
                        'file_size': backup_file.stat().st_size
                    })
                except Exception as e:
                    self.logger.warning(f"读取备份文件失败: {backup_file}, {e}")
                    continue
            
            # 按时间排序
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"列出备份失败: {e}")
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除注册表备份"""
        try:
            backup_file = self.backup_dir / f"{backup_id}.json"
            
            if backup_file.exists():
                backup_file.unlink()
                self.logger.info(f"删除注册表备份: {backup_id}")
                return True
            else:
                self.logger.warning(f"备份文件不存在: {backup_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"删除备份失败: {e}")
            return False
    
    def cleanup_old_backups(self, max_backups: int = None) -> int:
        """清理旧的备份文件"""
        try:
            if max_backups is None:
                max_backups = self.config_manager.get_max_backup_count()
            
            backups = self.list_backups()
            
            if len(backups) <= max_backups:
                return 0
            
            # 删除多余的备份
            deleted_count = 0
            for backup in backups[max_backups:]:
                if self.delete_backup(backup['backup_id']):
                    deleted_count += 1
            
            self.logger.info(f"清理了 {deleted_count} 个旧备份")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理备份失败: {e}")
            return 0

# 全局注册表管理器实例
_registry_manager: Optional[RegistryManager] = None

def get_registry_manager() -> RegistryManager:
    """获取全局注册表管理器实例"""
    global _registry_manager
    if _registry_manager is None:
        _registry_manager = RegistryManager()
    return _registry_manager
