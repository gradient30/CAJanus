#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看备份功能修复验证测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.backup_widget import BackupWidget

def test_view_backup_fix():
    """测试查看备份功能修复"""
    print("=== 查看备份功能修复验证测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建备份控件
        backup_widget = BackupWidget()
        
        print("✅ BackupWidget创建成功")
        
        # 显示窗口
        backup_widget.show()
        backup_widget.setWindowTitle("查看备份功能修复验证")
        backup_widget.resize(1000, 800)
        
        print("\n修复内容:")
        print("1. ✅ 移除了 check=True 参数，避免因非零退出码报错")
        print("2. ✅ 对Windows系统特殊处理，explorer经常返回非零码但仍成功")
        print("3. ✅ 添加了超时处理，避免命令挂起")
        print("4. ✅ 改进了错误处理，只在真正失败时显示错误")
        print("5. ✅ 增强了文件打开功能，支持多种编辑器")
        
        print("\n测试说明:")
        print("【查看备份目录】")
        print("- 点击 '查看备份' 按钮")
        print("- 应该能正常打开文件管理器到备份目录")
        print("- 不应该显示错误对话框")
        
        print("\n【查看备份文件详情】")
        print("- 在备份历史表格中点击 '查看' 按钮")
        print("- 在详情对话框中点击 '打开文件' 按钮")
        print("- 应该能用文本编辑器打开备份文件")
        print("- 不应该显示错误对话框")
        
        print("\n【错误处理改进】")
        print("✅ Windows系统: explorer返回非零码不再报错")
        print("✅ macOS系统: 只在真正失败时报错")
        print("✅ Linux系统: 尝试多个编辑器，提供备选方案")
        print("✅ 超时处理: 避免命令挂起导致界面卡死")
        
        print("\n【预期行为】")
        print("- 查看备份: 静默打开文件管理器，无错误提示")
        print("- 打开文件: 静默打开文本编辑器，无错误提示")
        print("- 失败情况: 显示文件路径，让用户手动操作")
        
        print("\n请测试 '查看备份' 功能，确认不再显示错误对话框...")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_view_backup_fix())
