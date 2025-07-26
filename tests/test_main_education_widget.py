#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序教育功能测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.education_widget import EducationWidget

def test_main_education_widget():
    """测试主程序教育功能"""
    print("=== 主程序教育功能测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建教育功能主控件
        education_widget = EducationWidget()
        
        print("✅ EducationWidget主控件创建成功")
        
        # 检查标签页数量
        tab_count = education_widget.tab_widget.count()
        print(f"标签页数量: {tab_count}")
        
        for i in range(tab_count):
            tab_name = education_widget.tab_widget.tabText(i)
            print(f"  标签页 {i}: {tab_name}")
        
        # 测试操作指导标签页
        print("\n测试操作指导标签页:")
        education_widget.tab_widget.setCurrentIndex(1)  # 操作指导
        guide_widget = education_widget.guide_widget
        
        # 检查操作指导控件
        if hasattr(guide_widget, 'operations_tree'):
            tree_count = guide_widget.operations_tree.topLevelItemCount()
            print(f"  操作指导树形控件项目数: {tree_count}")
            
            if tree_count > 0:
                # 展开第一个分类
                category_item = guide_widget.operations_tree.topLevelItem(0)
                category_item.setExpanded(True)
                print(f"  第一个分类: {category_item.text(0)}")
                
                if category_item.childCount() > 0:
                    # 选择第一个操作
                    operation_item = category_item.child(0)
                    guide_widget.operations_tree.setCurrentItem(operation_item)
                    print(f"  第一个操作: {operation_item.text(0)}")
                    
                    # 模拟点击
                    guide_widget.on_operation_selected(operation_item, 0)
                    
                    # 检查内容
                    title_text = guide_widget.content_title.text()
                    content_text = guide_widget.guide_text.toPlainText()
                    print(f"  标题: {title_text}")
                    print(f"  内容长度: {len(content_text)} 字符")
                    
                    if len(content_text) > 0:
                        print("  ✅ 操作指导内容显示正常")
                    else:
                        print("  ❌ 操作指导内容为空")
                        print("  尝试调试...")
                        
                        # 检查数据结构
                        if hasattr(guide_widget, 'guides'):
                            print(f"  guides数据结构存在，键: {list(guide_widget.guides.keys())}")
                        else:
                            print("  ❌ guides数据结构不存在")
        else:
            print("  ❌ operations_tree属性不存在")
        
        # 测试学习资源标签页
        print("\n测试学习资源标签页:")
        education_widget.tab_widget.setCurrentIndex(2)  # 学习资源
        resources_widget = education_widget.resources_widget
        
        # 检查学习资源控件
        if hasattr(resources_widget, 'resources_tree'):
            tree_count = resources_widget.resources_tree.topLevelItemCount()
            print(f"  学习资源树形控件项目数: {tree_count}")
            
            if tree_count > 0:
                # 展开第一个分类
                category_item = resources_widget.resources_tree.topLevelItem(0)
                category_item.setExpanded(True)
                print(f"  第一个分类: {category_item.text(0)}")
                
                if category_item.childCount() > 0:
                    # 选择第一个资源
                    resource_item = category_item.child(0)
                    resources_widget.resources_tree.setCurrentItem(resource_item)
                    print(f"  第一个资源: {resource_item.text(0)}")
                    
                    # 模拟点击
                    resources_widget.on_resource_selected(resource_item, 0)
                    
                    # 检查内容
                    title_text = resources_widget.content_title.text()
                    content_text = resources_widget.resources_text.toPlainText()
                    print(f"  标题: {title_text}")
                    print(f"  内容长度: {len(content_text)} 字符")
                    
                    if len(content_text) > 0:
                        print("  ✅ 学习资源内容显示正常")
                    else:
                        print("  ❌ 学习资源内容为空")
                        print("  尝试调试...")
                        
                        # 检查数据结构
                        if hasattr(resources_widget, 'resources'):
                            print(f"  resources数据结构存在，键: {list(resources_widget.resources.keys())}")
                        else:
                            print("  ❌ resources数据结构不存在")
        else:
            print("  ❌ resources_tree属性不存在")
        
        # 显示窗口
        print("\n显示主教育功能窗口:")
        education_widget.show()
        education_widget.setWindowTitle("主程序教育功能测试")
        education_widget.resize(1000, 700)
        
        print("✅ 窗口已显示，请手动测试各个标签页的内容显示")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_main_education_widget())
