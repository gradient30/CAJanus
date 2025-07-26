#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备指纹识别与修改工具 (Janus) - GUI版本
高级教学与安全研究平台

本工具旨在帮助用户理解设备指纹识别技术的原理和实现方式，
通过实际操作加深对系统安全机制的理解。

作者: 作为教育工作者的开发团队
版本: 2.0
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

from core.logger import get_logger
from core.config_manager import ConfigManager
from ui.main_window import MainWindow


class JanusApplication:
    """Janus应用程序类"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.splash = None
        self.logger = get_logger("janus_app")
        self.config_manager = ConfigManager()
    
    def init_application(self):
        """初始化应用程序"""
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        
        # 设置应用程序信息
        self.app.setApplicationName(self.config_manager.get_config('app.name', '设备指纹识别与修改工具'))
        self.app.setApplicationVersion(self.config_manager.get_config('app.version', '2.0'))
        self.app.setOrganizationName("Janus Development Team")
        
        # 设置应用程序字体
        font = QFont("Microsoft YaHei UI", 9)
        self.app.setFont(font)
        
        self.logger.info("应用程序初始化完成")
    
    def show_splash_screen(self):
        """显示启动画面"""
        # 创建启动画面
        splash_pixmap = self.create_splash_pixmap()
        self.splash = QSplashScreen(splash_pixmap)
        self.splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        
        # 显示启动画面
        self.splash.show()
        self.app.processEvents()
        
        # 显示加载信息
        self.splash.showMessage("正在初始化...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        self.app.processEvents()
        
        self.logger.info("启动画面显示完成")
    
    def create_splash_pixmap(self):
        """创建启动画面图片"""
        # 尝试加载启动画面图片
        splash_paths = [
            "resources/images/splash.png",
            "assets/splash.png"
        ]
        
        for splash_path in splash_paths:
            if os.path.exists(splash_path):
                return QPixmap(splash_path)
        
        # 如果没有找到图片，创建一个简单的启动画面
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.darkBlue)
        return pixmap
    
    def check_system_requirements(self):
        """检查系统要求"""
        try:
            # 检查Python版本
            if sys.version_info < (3, 8):
                self.show_error("系统要求错误", 
                              f"需要Python 3.8或更高版本\n当前版本: {sys.version}")
                return False
            
            # 检查PyQt5
            try:
                from PyQt5.QtCore import QT_VERSION_STR
                self.logger.info(f"PyQt5版本: {QT_VERSION_STR}")
            except ImportError:
                self.show_error("依赖错误", "未找到PyQt5，请先安装PyQt5")
                return False
            
            # 检查核心模块
            try:
                from core.platform_factory import get_platform_factory
                factory = get_platform_factory()
                self.logger.info(f"平台支持: {factory.current_platform}")
            except Exception as e:
                self.show_error("核心模块错误", f"核心模块加载失败: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.show_error("系统检查错误", f"系统要求检查失败: {e}")
            return False
    
    def show_error(self, title: str, message: str):
        """显示错误对话框"""
        if self.app:
            QMessageBox.critical(None, title, message)
        else:
            print(f"错误: {title} - {message}")
    
    def load_main_window(self):
        """加载主窗口"""
        try:
            if self.splash:
                self.splash.showMessage("正在加载主界面...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
                self.app.processEvents()
            
            # 创建主窗口
            self.main_window = MainWindow()
            
            if self.splash:
                self.splash.showMessage("初始化完成", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
                self.app.processEvents()
            
            self.logger.info("主窗口加载完成")
            return True
            
        except Exception as e:
            self.logger.error(f"主窗口加载失败: {e}")
            self.show_error("界面加载错误", f"主界面加载失败: {e}")
            return False
    
    def show_main_window(self):
        """显示主窗口"""
        if self.main_window:
            # 关闭启动画面
            if self.splash:
                self.splash.finish(self.main_window)
            
            # 显示主窗口
            self.main_window.show()
            self.logger.info("主窗口显示完成")
    
    def run(self):
        """运行应用程序"""
        try:
            # 初始化应用程序
            self.init_application()
            
            # 检查系统要求
            if not self.check_system_requirements():
                return 1
            
            # 显示启动画面
            self.show_splash_screen()
            
            # 模拟加载时间
            QTimer.singleShot(1000, self.delayed_load)
            
            # 运行应用程序
            return self.app.exec_()
            
        except Exception as e:
            self.logger.error(f"应用程序运行失败: {e}")
            self.show_error("应用程序错误", f"应用程序运行失败: {e}")
            return 1
    
    def delayed_load(self):
        """延迟加载主窗口"""
        if self.load_main_window():
            QTimer.singleShot(500, self.show_main_window)
        else:
            if self.splash:
                self.splash.close()
            self.app.quit()


def main():
    """主函数"""
    # 设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建并运行应用程序
    janus_app = JanusApplication()
    return janus_app.run()


if __name__ == "__main__":
    sys.exit(main())
