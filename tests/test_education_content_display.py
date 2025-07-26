#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教育功能内容显示测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.education_widget import OperationGuideWidget, LearningResourcesWidget

def test_education_content_display():
    """测试教育功能内容显示"""
    print("=== 教育功能内容显示测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 测试操作指导控件
        print("\n1. 测试操作指导控件:")
        operation_widget = OperationGuideWidget()
        
        # 检查树形控件是否有内容
        tree_count = operation_widget.operations_tree.topLevelItemCount()
        print(f"  操作指导树形控件项目数: {tree_count}")
        
        if tree_count > 0:
            # 获取第一个分类项
            category_item = operation_widget.operations_tree.topLevelItem(0)
            print(f"  第一个分类: {category_item.text(0)}")
            
            if category_item.childCount() > 0:
                # 获取第一个操作项
                operation_item = category_item.child(0)
                print(f"  第一个操作: {operation_item.text(0)}")
                
                # 模拟点击事件
                print("  模拟点击第一个操作项...")
                operation_widget.on_operation_selected(operation_item, 0)
                
                # 检查内容是否显示
                title_text = operation_widget.content_title.text()
                content_text = operation_widget.guide_text.toPlainText()
                print(f"  标题显示: {title_text}")
                print(f"  内容长度: {len(content_text)} 字符")
                
                if len(content_text) > 0:
                    print("  ✅ 操作指导内容显示正常")
                else:
                    print("  ❌ 操作指导内容为空")
            else:
                print("  ❌ 分类下没有操作项")
        else:
            print("  ❌ 操作指导树形控件为空")
        
        # 测试学习资源控件
        print("\n2. 测试学习资源控件:")
        resource_widget = LearningResourcesWidget()
        
        # 检查树形控件是否有内容
        tree_count = resource_widget.resources_tree.topLevelItemCount()
        print(f"  学习资源树形控件项目数: {tree_count}")
        
        if tree_count > 0:
            # 获取第一个分类项
            category_item = resource_widget.resources_tree.topLevelItem(0)
            print(f"  第一个分类: {category_item.text(0)}")
            
            if category_item.childCount() > 0:
                # 获取第一个资源项
                resource_item = category_item.child(0)
                print(f"  第一个资源: {resource_item.text(0)}")
                
                # 模拟点击事件
                print("  模拟点击第一个资源项...")
                resource_widget.on_resource_selected(resource_item, 0)
                
                # 检查内容是否显示
                title_text = resource_widget.content_title.text()
                content_text = resource_widget.resources_text.toPlainText()
                print(f"  标题显示: {title_text}")
                print(f"  内容长度: {len(content_text)} 字符")
                
                if len(content_text) > 0:
                    print("  ✅ 学习资源内容显示正常")
                else:
                    print("  ❌ 学习资源内容为空")
            else:
                print("  ❌ 分类下没有资源项")
        else:
            print("  ❌ 学习资源树形控件为空")
        
        # 显示窗口进行手动测试
        print("\n3. 显示窗口进行手动测试:")
        operation_widget.show()
        operation_widget.setWindowTitle("操作指导测试")
        operation_widget.resize(800, 600)
        operation_widget.move(100, 100)
        
        resource_widget.show()
        resource_widget.setWindowTitle("学习资源测试")
        resource_widget.resize(800, 600)
        resource_widget.move(950, 100)
        
        print("  ✅ 两个窗口已显示，请手动点击左侧树形控件测试")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_education_content_display())
