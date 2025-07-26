#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份GUI功能测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.backup_widget import BackupWidget, BackupHistoryWidget

def test_backup_gui():
    """测试备份GUI功能"""
    print("=== 备份GUI功能测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 测试1: 创建BackupHistoryWidget
        print("\n1. 测试BackupHistoryWidget:")
        history_widget = BackupHistoryWidget()
        
        # 检查表格行数
        row_count = history_widget.history_table.rowCount()
        print(f"  表格行数: {row_count}")
        
        if row_count > 0:
            print("  表格内容:")
            for row in range(row_count):
                time_item = history_widget.history_table.item(row, 0)
                type_item = history_widget.history_table.item(row, 1)
                size_item = history_widget.history_table.item(row, 2)
                status_item = history_widget.history_table.item(row, 3)
                
                time_text = time_item.text() if time_item else "N/A"
                type_text = type_item.text() if type_item else "N/A"
                size_text = size_item.text() if size_item else "N/A"
                status_text = status_item.text() if status_item else "N/A"
                
                print(f"    行 {row}: {time_text} | {type_text} | {size_text} | {status_text}")
        else:
            print("  ⚠️  表格为空")
        
        # 测试2: 手动调用load_backup_history
        print("\n2. 手动调用load_backup_history:")
        history_widget.load_backup_history()
        
        new_row_count = history_widget.history_table.rowCount()
        print(f"  刷新后表格行数: {new_row_count}")
        
        if new_row_count > 0:
            print("  刷新后表格内容:")
            for row in range(new_row_count):
                time_item = history_widget.history_table.item(row, 0)
                type_item = history_widget.history_table.item(row, 1)
                size_item = history_widget.history_table.item(row, 2)
                status_item = history_widget.history_table.item(row, 3)
                
                time_text = time_item.text() if time_item else "N/A"
                type_text = type_item.text() if type_item else "N/A"
                size_text = size_item.text() if size_item else "N/A"
                status_text = status_item.text() if status_item else "N/A"
                
                print(f"    行 {row}: {time_text} | {type_text} | {size_text} | {status_text}")
        else:
            print("  ⚠️  刷新后表格仍为空")
        
        # 测试3: 创建完整的BackupWidget
        print("\n3. 测试完整的BackupWidget:")
        backup_widget = BackupWidget()
        
        # 检查history_widget是否存在
        if hasattr(backup_widget, 'history_widget'):
            history_row_count = backup_widget.history_widget.history_table.rowCount()
            print(f"  BackupWidget中的历史表格行数: {history_row_count}")
            
            if history_row_count > 0:
                print("  BackupWidget中的表格内容:")
                for row in range(min(3, history_row_count)):  # 只显示前3行
                    time_item = backup_widget.history_widget.history_table.item(row, 0)
                    type_item = backup_widget.history_widget.history_table.item(row, 1)
                    size_item = backup_widget.history_widget.history_table.item(row, 2)
                    
                    time_text = time_item.text() if time_item else "N/A"
                    type_text = type_item.text() if type_item else "N/A"
                    size_text = size_item.text() if size_item else "N/A"
                    
                    print(f"    行 {row}: {time_text} | {type_text} | {size_text}")
        else:
            print("  ❌ BackupWidget中没有history_widget属性")
        
        # 显示窗口进行手动测试
        print("\n4. 显示窗口进行手动测试:")
        print("  正在显示BackupWidget窗口...")
        print("  请检查备份历史是否正确显示")
        
        backup_widget.show()
        backup_widget.setWindowTitle("备份功能测试")
        backup_widget.resize(800, 600)
        
        print("  ✅ 窗口已显示，请手动检查")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_backup_gui())
