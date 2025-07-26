#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帮助系统功能测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.help_system import HelpSystemDialog

def test_help_system():
    """测试帮助系统"""
    app = QApplication(sys.argv)
    
    # 创建帮助系统对话框
    help_dialog = HelpSystemDialog()
    help_dialog.show()
    
    print("帮助系统测试:")
    print("1. 帮助对话框已打开")
    print("2. 请测试快速链接按钮功能")
    print("3. 检查帮助内容是否正确显示")
    print("4. 测试最近查看功能")
    print("5. 测试打印功能")
    
    # 运行应用程序
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_help_system())
