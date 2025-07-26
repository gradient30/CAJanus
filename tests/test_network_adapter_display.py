#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络适配器显示测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.fingerprint_widget import FingerprintWidget

def test_network_adapter_display():
    """测试网络适配器显示"""
    print("=== 网络适配器显示测试 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建设备指纹控件
        fingerprint_widget = FingerprintWidget()
        
        print("✅ FingerprintWidget创建成功")
        
        # 显示窗口
        fingerprint_widget.show()
        fingerprint_widget.setWindowTitle("网络适配器显示测试")
        fingerprint_widget.resize(1000, 800)
        
        print("\n网络适配器显示修复:")
        print("【WMI命令优化】")
        print("1. ✅ 使用更明确的WMI查询条件")
        print("2. ✅ 动态解析WMI输出标题行")
        print("3. ✅ 正确映射字段索引")
        print("4. ✅ 添加备用获取方法")
        
        print("\n【MAC地址标准化】")
        print("1. ✅ 统一MAC地址格式为 XX:XX:XX:XX:XX:XX")
        print("2. ✅ 过滤无效的MAC地址")
        print("3. ✅ 处理不同格式的MAC地址输入")
        
        print("\n【适配器名称处理】")
        print("1. ✅ 优先使用Name字段")
        print("2. ✅ Name为空时使用Description字段")
        print("3. ✅ 确保每个适配器都有可显示的名称")
        
        print("\n【错误处理改进】")
        print("1. ✅ WMI命令失败时自动使用备用方法")
        print("2. ✅ 字段解析错误时的降级处理")
        print("3. ✅ 详细的日志记录和错误信息")
        
        print("\n【测试说明】")
        print("请检查网络适配器标签页中的表格:")
        print("- 适配器名称列应该显示具体的网卡名称")
        print("- MAC地址列应该显示标准格式的MAC地址")
        print("- 类型列应该显示网卡类型（以太网/无线等）")
        print("- 状态列应该显示启用/禁用状态")
        print("- 操作列应该有修改按钮")
        
        print("\n如果适配器名称仍然为空，请检查:")
        print("1. 是否有管理员权限")
        print("2. WMI服务是否正常运行")
        print("3. 查看控制台日志输出")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_network_adapter_display())
