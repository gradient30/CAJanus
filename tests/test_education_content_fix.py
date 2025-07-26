#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教育功能内容显示修复测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.education_widget import EducationWidget

def test_education_content_fix():
    """测试教育功能内容显示修复"""
    print("=== 教育功能内容显示修复测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建教育功能控件
        education_widget = EducationWidget()
        
        print("✅ EducationWidget创建成功")
        
        # 显示窗口
        education_widget.show()
        education_widget.setWindowTitle("教育功能内容显示修复测试")
        education_widget.resize(1200, 800)
        
        print("\n修复内容:")
        print("1. ✅ 将setMarkdown()改为setPlainText()，解决PyQt5兼容性问题")
        print("2. ✅ 操作指导和学习资源的右侧内容现在应该正常显示")
        print("3. ✅ 保持了统一的树形+分割器布局")
        
        print("\n测试说明:")
        print("请依次测试以下功能:")
        print("1. 点击'操作指导'标签页")
        print("   - 点击左侧树形结构中的任意操作项")
        print("   - 右侧应该显示详细的操作指导内容")
        print("2. 点击'学习资源'标签页")
        print("   - 点击左侧树形结构中的任意资源项")
        print("   - 右侧应该显示详细的资源内容")
        print("3. 点击'原理解释'标签页")
        print("   - 确认原有功能正常工作")
        
        print("\n预期结果:")
        print("- 所有标签页的右侧内容区域都应该正常显示文本")
        print("- 点击左侧树形结构时，右侧内容应该立即更新")
        print("- 标题应该显示当前选择的项目名称")
        
        print("\n如果内容仍然不显示，可能的原因:")
        print("1. 数据加载问题 - 检查控制台是否有错误信息")
        print("2. 事件绑定问题 - 确认点击事件是否正确触发")
        print("3. 控件初始化问题 - 检查控件是否正确创建")
        
        # 自动测试操作指导
        print("\n自动测试操作指导:")
        education_widget.tab_widget.setCurrentIndex(1)  # 切换到操作指导
        guide_widget = education_widget.guide_widget
        
        if guide_widget.operations_tree.topLevelItemCount() > 0:
            # 展开第一个分类并选择第一个操作
            category_item = guide_widget.operations_tree.topLevelItem(0)
            category_item.setExpanded(True)
            
            if category_item.childCount() > 0:
                operation_item = category_item.child(0)
                guide_widget.operations_tree.setCurrentItem(operation_item)
                guide_widget.on_operation_selected(operation_item, 0)
                
                # 检查内容是否显示
                content_text = guide_widget.guide_text.toPlainText()
                if len(content_text) > 0:
                    print(f"  ✅ 操作指导内容正常显示 ({len(content_text)} 字符)")
                else:
                    print("  ❌ 操作指导内容仍然为空")
        
        # 自动测试学习资源
        print("\n自动测试学习资源:")
        education_widget.tab_widget.setCurrentIndex(2)  # 切换到学习资源
        resources_widget = education_widget.resources_widget
        
        if resources_widget.resources_tree.topLevelItemCount() > 0:
            # 展开第一个分类并选择第一个资源
            category_item = resources_widget.resources_tree.topLevelItem(0)
            category_item.setExpanded(True)
            
            if category_item.childCount() > 0:
                resource_item = category_item.child(0)
                resources_widget.resources_tree.setCurrentItem(resource_item)
                resources_widget.on_resource_selected(resource_item, 0)
                
                # 检查内容是否显示
                content_text = resources_widget.resources_text.toPlainText()
                if len(content_text) > 0:
                    print(f"  ✅ 学习资源内容正常显示 ({len(content_text)} 字符)")
                else:
                    print("  ❌ 学习资源内容仍然为空")
        
        print("\n✅ 自动测试完成，请手动验证界面显示效果")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_education_content_fix())
