#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际化管理器
支持多语言界面和本地化功能
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from enum import Enum
from datetime import datetime

from core.logger import get_logger


class SupportedLanguage(Enum):
    """支持的语言"""
    ZH_CN = "zh_CN"  # 简体中文
    EN_US = "en_US"  # 英语
    ZH_TW = "zh_TW"  # 繁体中文
    JA_JP = "ja_JP"  # 日语


class I18nManager:
    """国际化管理器"""
    
    def __init__(self):
        self.logger = get_logger("i18n_manager")
        self.current_language = SupportedLanguage.ZH_CN
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_language = SupportedLanguage.ZH_CN
        
        # 语言资源目录
        self.resources_dir = Path("resources/i18n")
        self.resources_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化翻译资源
        self._init_translation_resources()
        self._load_translations()
    
    def _init_translation_resources(self):
        """初始化翻译资源文件"""
        try:
            # 创建默认的中文翻译文件
            zh_cn_file = self.resources_dir / "zh_CN.json"
            if not zh_cn_file.exists():
                zh_cn_translations = self._get_default_zh_cn_translations()
                with open(zh_cn_file, 'w', encoding='utf-8') as f:
                    json.dump(zh_cn_translations, f, ensure_ascii=False, indent=2)
            
            # 创建英文翻译文件模板
            en_us_file = self.resources_dir / "en_US.json"
            if not en_us_file.exists():
                en_us_translations = self._get_default_en_us_translations()
                with open(en_us_file, 'w', encoding='utf-8') as f:
                    json.dump(en_us_translations, f, ensure_ascii=False, indent=2)
            
            self.logger.info("翻译资源文件初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化翻译资源失败: {e}")
    
    def _get_default_zh_cn_translations(self) -> Dict[str, str]:
        """获取默认中文翻译"""
        return {
            # 应用程序基本信息
            "app.name": "设备指纹识别与修改工具",
            "app.version": "版本",
            "app.description": "用于教学和研究的设备指纹识别与修改工具",
            
            # 菜单项
            "menu.file": "文件",
            "menu.file.new": "新建",
            "menu.file.open": "打开",
            "menu.file.save": "保存",
            "menu.file.exit": "退出",
            "menu.tools": "工具",
            "menu.tools.settings": "设置",
            "menu.tools.refresh": "刷新",
            "menu.help": "帮助",
            "menu.help.about": "关于",
            "menu.help.help": "帮助文档",
            
            # 标签页
            "tab.system_status": "系统状态",
            "tab.fingerprint": "设备指纹",
            "tab.backup": "备份管理",
            "tab.education": "教育功能",
            
            # 按钮
            "button.ok": "确定",
            "button.cancel": "取消",
            "button.apply": "应用",
            "button.close": "关闭",
            "button.refresh": "刷新",
            "button.backup": "备份",
            "button.restore": "恢复",
            "button.modify": "修改",
            "button.reset": "重置",
            
            # 状态信息
            "status.ready": "就绪",
            "status.loading": "加载中...",
            "status.processing": "处理中...",
            "status.completed": "完成",
            "status.failed": "失败",
            "status.error": "错误",
            
            # 系统信息
            "system.os": "操作系统",
            "system.version": "版本",
            "system.architecture": "架构",
            "system.hostname": "主机名",
            "system.username": "用户名",
            "system.uptime": "运行时间",
            
            # 网络信息
            "network.adapter": "网络适配器",
            "network.mac_address": "MAC地址",
            "network.ip_address": "IP地址",
            "network.status": "状态",
            "network.connected": "已连接",
            "network.disconnected": "未连接",
            
            # 硬件信息
            "hardware.cpu": "处理器",
            "hardware.memory": "内存",
            "hardware.disk": "磁盘",
            "hardware.machine_guid": "机器GUID",
            "hardware.volume_serial": "卷序列号",
            
            # 确认对话框
            "confirm.title": "确认操作",
            "confirm.message": "您确定要执行此操作吗？",
            "confirm.warning": "警告",
            "confirm.risk_high": "高风险操作",
            "confirm.risk_medium": "中等风险操作",
            "confirm.risk_low": "低风险操作",
            
            # 错误信息
            "error.general": "发生错误",
            "error.permission_denied": "权限不足",
            "error.file_not_found": "文件未找到",
            "error.network_error": "网络错误",
            "error.invalid_input": "输入无效",
            
            # 设置对话框
            "settings.title": "设置",
            "settings.general": "常规",
            "settings.security": "安全",
            "settings.advanced": "高级",
            "settings.language": "语言",
            "settings.theme": "主题",
            "settings.font_size": "字体大小",
            
            # 帮助系统
            "help.title": "帮助系统",
            "help.quick_start": "快速入门",
            "help.user_guide": "用户指南",
            "help.faq": "常见问题",
            "help.about": "关于软件",
            
            # 日期时间格式
            "datetime.format.date": "YYYY年MM月DD日",
            "datetime.format.time": "HH:mm:ss",
            "datetime.format.datetime": "YYYY年MM月DD日 HH:mm:ss",
            
            # 单位
            "unit.bytes": "字节",
            "unit.kb": "KB",
            "unit.mb": "MB",
            "unit.gb": "GB",
            "unit.seconds": "秒",
            "unit.minutes": "分钟",
            "unit.hours": "小时",
            "unit.days": "天"
        }
    
    def _get_default_en_us_translations(self) -> Dict[str, str]:
        """获取默认英文翻译"""
        return {
            # Application basic information
            "app.name": "Device Fingerprint Identification & Modification Tool",
            "app.version": "Version",
            "app.description": "Device fingerprint identification and modification tool for education and research",
            
            # Menu items
            "menu.file": "File",
            "menu.file.new": "New",
            "menu.file.open": "Open",
            "menu.file.save": "Save",
            "menu.file.exit": "Exit",
            "menu.tools": "Tools",
            "menu.tools.settings": "Settings",
            "menu.tools.refresh": "Refresh",
            "menu.help": "Help",
            "menu.help.about": "About",
            "menu.help.help": "Help Documentation",
            
            # Tabs
            "tab.system_status": "System Status",
            "tab.fingerprint": "Device Fingerprint",
            "tab.backup": "Backup Management",
            "tab.education": "Education Features",
            
            # Buttons
            "button.ok": "OK",
            "button.cancel": "Cancel",
            "button.apply": "Apply",
            "button.close": "Close",
            "button.refresh": "Refresh",
            "button.backup": "Backup",
            "button.restore": "Restore",
            "button.modify": "Modify",
            "button.reset": "Reset",
            
            # Status information
            "status.ready": "Ready",
            "status.loading": "Loading...",
            "status.processing": "Processing...",
            "status.completed": "Completed",
            "status.failed": "Failed",
            "status.error": "Error",
            
            # System information
            "system.os": "Operating System",
            "system.version": "Version",
            "system.architecture": "Architecture",
            "system.hostname": "Hostname",
            "system.username": "Username",
            "system.uptime": "Uptime",
            
            # Network information
            "network.adapter": "Network Adapter",
            "network.mac_address": "MAC Address",
            "network.ip_address": "IP Address",
            "network.status": "Status",
            "network.connected": "Connected",
            "network.disconnected": "Disconnected",
            
            # Hardware information
            "hardware.cpu": "Processor",
            "hardware.memory": "Memory",
            "hardware.disk": "Disk",
            "hardware.machine_guid": "Machine GUID",
            "hardware.volume_serial": "Volume Serial",
            
            # Confirmation dialog
            "confirm.title": "Confirm Operation",
            "confirm.message": "Are you sure you want to perform this operation?",
            "confirm.warning": "Warning",
            "confirm.risk_high": "High Risk Operation",
            "confirm.risk_medium": "Medium Risk Operation",
            "confirm.risk_low": "Low Risk Operation",
            
            # Error messages
            "error.general": "An error occurred",
            "error.permission_denied": "Permission denied",
            "error.file_not_found": "File not found",
            "error.network_error": "Network error",
            "error.invalid_input": "Invalid input",
            
            # Settings dialog
            "settings.title": "Settings",
            "settings.general": "General",
            "settings.security": "Security",
            "settings.advanced": "Advanced",
            "settings.language": "Language",
            "settings.theme": "Theme",
            "settings.font_size": "Font Size",
            
            # Help system
            "help.title": "Help System",
            "help.quick_start": "Quick Start",
            "help.user_guide": "User Guide",
            "help.faq": "FAQ",
            "help.about": "About",
            
            # Date time format
            "datetime.format.date": "MM/DD/YYYY",
            "datetime.format.time": "HH:mm:ss",
            "datetime.format.datetime": "MM/DD/YYYY HH:mm:ss",
            
            # Units
            "unit.bytes": "Bytes",
            "unit.kb": "KB",
            "unit.mb": "MB",
            "unit.gb": "GB",
            "unit.seconds": "Seconds",
            "unit.minutes": "Minutes",
            "unit.hours": "Hours",
            "unit.days": "Days"
        }
    
    def _load_translations(self):
        """加载所有翻译文件"""
        try:
            for language in SupportedLanguage:
                translation_file = self.resources_dir / f"{language.value}.json"
                if translation_file.exists():
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[language.value] = json.load(f)
                    self.logger.debug(f"加载翻译文件: {language.value}")
                else:
                    self.logger.warning(f"翻译文件不存在: {translation_file}")
            
            self.logger.info(f"加载了 {len(self.translations)} 个语言包")
            
        except Exception as e:
            self.logger.error(f"加载翻译文件失败: {e}")
    
    def set_language(self, language: SupportedLanguage):
        """设置当前语言"""
        if language.value in self.translations:
            self.current_language = language
            self.logger.info(f"切换语言到: {language.value}")
        else:
            self.logger.warning(f"不支持的语言: {language.value}")
    
    def get_text(self, key: str, **kwargs) -> str:
        """获取翻译文本"""
        try:
            # 尝试获取当前语言的翻译
            current_translations = self.translations.get(self.current_language.value, {})
            text = current_translations.get(key)
            
            # 如果当前语言没有翻译，尝试使用回退语言
            if text is None:
                fallback_translations = self.translations.get(self.fallback_language.value, {})
                text = fallback_translations.get(key)
            
            # 如果仍然没有翻译，返回键名
            if text is None:
                self.logger.warning(f"未找到翻译: {key}")
                return key
            
            # 处理参数替换
            if kwargs:
                try:
                    text = text.format(**kwargs)
                except Exception as e:
                    self.logger.error(f"翻译参数替换失败: {e}")
            
            return text
            
        except Exception as e:
            self.logger.error(f"获取翻译文本失败: {e}")
            return key
    
    def format_datetime(self, dt: datetime, format_type: str = "datetime") -> str:
        """格式化日期时间"""
        try:
            format_key = f"datetime.format.{format_type}"
            format_string = self.get_text(format_key)
            
            # 转换格式字符串
            if self.current_language == SupportedLanguage.ZH_CN:
                # 中文格式
                format_string = format_string.replace("YYYY", "%Y")
                format_string = format_string.replace("MM", "%m")
                format_string = format_string.replace("DD", "%d")
                format_string = format_string.replace("HH", "%H")
                format_string = format_string.replace("mm", "%M")
                format_string = format_string.replace("ss", "%S")
            else:
                # 英文格式
                format_string = format_string.replace("MM", "%m")
                format_string = format_string.replace("DD", "%d")
                format_string = format_string.replace("YYYY", "%Y")
                format_string = format_string.replace("HH", "%H")
                format_string = format_string.replace("mm", "%M")
                format_string = format_string.replace("ss", "%S")
            
            return dt.strftime(format_string)
            
        except Exception as e:
            self.logger.error(f"格式化日期时间失败: {e}")
            return str(dt)
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        try:
            if size_bytes < 1024:
                return f"{size_bytes} {self.get_text('unit.bytes')}"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} {self.get_text('unit.kb')}"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} {self.get_text('unit.mb')}"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} {self.get_text('unit.gb')}"
        except Exception as e:
            self.logger.error(f"格式化文件大小失败: {e}")
            return f"{size_bytes} bytes"
    
    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return {
            SupportedLanguage.ZH_CN.value: "简体中文",
            SupportedLanguage.EN_US.value: "English",
            SupportedLanguage.ZH_TW.value: "繁體中文",
            SupportedLanguage.JA_JP.value: "日本語"
        }
    
    def get_current_language(self) -> SupportedLanguage:
        """获取当前语言"""
        return self.current_language


# 全局国际化管理器实例
_i18n_manager: Optional[I18nManager] = None

def get_i18n_manager() -> I18nManager:
    """获取全局国际化管理器实例"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager

def _(key: str, **kwargs) -> str:
    """快捷翻译函数"""
    return get_i18n_manager().get_text(key, **kwargs)
