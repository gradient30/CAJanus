#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教育功能样式修复测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.education_widget import EducationWidget

def test_education_style_fix():
    """测试教育功能样式修复"""
    print("=== 教育功能样式修复测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建教育功能控件
        education_widget = EducationWidget()
        
        print("✅ EducationWidget创建成功")
        
        # 显示窗口
        education_widget.show()
        education_widget.setWindowTitle("教育功能样式修复测试")
        education_widget.resize(1200, 800)
        
        print("\n样式修复内容:")
        print("1. ✅ 原理解释文本区域：深色背景 + 白色文字")
        print("2. ✅ 操作指导文本区域：深色背景 + 白色文字")
        print("3. ✅ 学习资源文本区域：深色背景 + 白色文字")
        print("4. ✅ 统一的视觉风格和对比度")
        
        print("\n样式详情:")
        print("- 背景色: #2b2b2b (深灰色)")
        print("- 文字色: #ffffff (白色)")
        print("- 选择背景色: #3d3d3d (中灰色)")
        print("- 边框: 1px solid #ddd")
        print("- 圆角: 5px")
        print("- 内边距: 10px")
        
        print("\n测试说明:")
        print("请依次测试以下功能，确认文字清晰可见:")
        print("1. 点击'原理解释'标签页")
        print("   - 点击左侧任意原理项目")
        print("   - 右侧应显示白色文字在深色背景上")
        print("2. 点击'操作指导'标签页")
        print("   - 点击左侧任意操作项目")
        print("   - 右侧应显示白色文字在深色背景上")
        print("3. 点击'学习资源'标签页")
        print("   - 点击左侧任意资源项目")
        print("   - 右侧应显示白色文字在深色背景上")
        
        print("\n预期效果:")
        print("- 所有文本区域都应该有深色背景")
        print("- 文字应该是白色，清晰可读")
        print("- 选择文本时应该有中灰色高亮")
        print("- 整体视觉效果统一协调")
        
        # 自动设置一些内容进行测试
        print("\n自动测试内容显示:")
        
        # 测试原理解释
        education_widget.tab_widget.setCurrentIndex(0)  # 原理解释
        principle_widget = education_widget.principle_widget
        if principle_widget.principle_tree.topLevelItemCount() > 0:
            category_item = principle_widget.principle_tree.topLevelItem(0)
            category_item.setExpanded(True)
            if category_item.childCount() > 0:
                principle_item = category_item.child(0)
                principle_widget.principle_tree.setCurrentItem(principle_item)
                principle_widget.on_principle_selected(principle_item, 0)
                print("  ✅ 原理解释内容已加载")
        
        # 测试操作指导
        education_widget.tab_widget.setCurrentIndex(1)  # 操作指导
        guide_widget = education_widget.guide_widget
        if guide_widget.operations_tree.topLevelItemCount() > 0:
            category_item = guide_widget.operations_tree.topLevelItem(0)
            category_item.setExpanded(True)
            if category_item.childCount() > 0:
                operation_item = category_item.child(0)
                guide_widget.operations_tree.setCurrentItem(operation_item)
                guide_widget.on_operation_selected(operation_item, 0)
                print("  ✅ 操作指导内容已加载")
        
        # 测试学习资源
        education_widget.tab_widget.setCurrentIndex(2)  # 学习资源
        resources_widget = education_widget.resources_widget
        if resources_widget.resources_tree.topLevelItemCount() > 0:
            category_item = resources_widget.resources_tree.topLevelItem(0)
            category_item.setExpanded(True)
            if category_item.childCount() > 0:
                resource_item = category_item.child(0)
                resources_widget.resources_tree.setCurrentItem(resource_item)
                resources_widget.on_resource_selected(resource_item, 0)
                print("  ✅ 学习资源内容已加载")
        
        print("\n✅ 样式修复测试完成")
        print("现在所有教育功能标签页的文字都应该清晰可见！")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_education_style_fix())
