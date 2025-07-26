#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份浏览功能测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.backup_widget import BackupWidget

def test_backup_browse():
    """测试备份浏览功能"""
    print("=== 备份浏览功能测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建备份控件
        backup_widget = BackupWidget()
        
        print("✅ BackupWidget创建成功")
        
        # 显示窗口
        backup_widget.show()
        backup_widget.setWindowTitle("备份浏览功能测试")
        backup_widget.resize(900, 700)
        
        print("功能测试说明:")
        print("1. 点击'选择目录'按钮 - 选择备份目录")
        print("2. 点击'打开目录'按钮 - 在文件管理器中打开备份目录")
        print("3. 在备份历史表格中点击'查看'按钮 - 查看备份文件详情")
        print("4. 在详情对话框中点击'打开文件'按钮 - 用文本编辑器打开备份文件")
        
        print("\n备份目录结构说明:")
        print("backups/")
        print("├── backup_*.bak          # 主备份文件(JSON格式)")
        print("└── registry/")
        print("    └── registry_*.json   # 注册表备份文件")
        
        print("\nregistry目录中*.json文件的作用:")
        print("- 存储具体的注册表键值对数据")
        print("- 每个文件对应一次注册表操作的备份")
        print("- 包含备份ID、时间戳、注册表路径和所有值")
        print("- 用于精确恢复注册表修改")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_backup_browse())
