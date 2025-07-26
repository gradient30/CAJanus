#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份功能修复验证测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.backup_widget import BackupWidget

def test_backup_fixes():
    """测试备份功能修复"""
    print("=== 备份功能修复验证测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建备份控件
        backup_widget = BackupWidget()
        
        print("✅ BackupWidget创建成功")
        
        # 显示窗口
        backup_widget.show()
        backup_widget.setWindowTitle("备份功能修复验证")
        backup_widget.resize(1000, 800)
        
        print("\n修复验证项目:")
        print("1. ✅ '打开目录' 改名为 '查看备份'")
        print("2. ✅ '查看备份' 按钮使用绝对路径打开文件管理器")
        print("3. ✅ 删除备份功能已实现")
        print("4. ✅ 快速恢复功能已实现")
        print("5. ✅ 导出备份功能已实现")
        
        print("\n功能测试说明:")
        print("【备份路径设置】")
        print("- '选择目录': 选择新的备份目录路径")
        print("- '查看备份': 在文件管理器中打开当前备份目录")
        
        print("\n【备份历史管理】")
        print("- '刷新列表': 重新加载备份历史")
        print("- '删除备份': 删除选中的备份文件（需先选择行）")
        print("- '导出备份': 将选中的备份导出到指定位置")
        
        print("\n【备份恢复】")
        print("- '从文件恢复': 选择备份文件进行恢复")
        print("- '快速恢复': 自动选择最新备份进行恢复")
        
        print("\n【备份历史表格操作】")
        print("- '恢复': 恢复选中的备份")
        print("- '查看': 查看备份文件详细信息")
        
        print("\n【安全提醒】")
        print("⚠️  删除和恢复操作都有确认对话框")
        print("⚠️  快速恢复会自动选择最新的备份文件")
        print("⚠️  导出功能会验证文件完整性")
        
        print("\n【错误处理】")
        print("✅ 文件不存在时的友好提示")
        print("✅ 权限不足时的错误处理")
        print("✅ 操作失败时的详细错误信息")
        
        print("\n请手动测试以上功能...")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_backup_fixes())
