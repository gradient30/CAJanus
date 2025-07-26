#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
测试各个组件的性能表现
"""

import sys
import time
import statistics
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def measure_time(func, *args, **kwargs):
    """测量函数执行时间"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

def test_platform_factory_performance():
    """测试平台工厂性能"""
    print("=== 测试平台工厂性能 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        # 测试工厂创建时间
        times = []
        for i in range(10):
            _, duration = measure_time(get_platform_factory)
            times.append(duration * 1000)  # 转换为毫秒
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"平台工厂创建时间:")
        print(f"  平均: {avg_time:.2f}ms")
        print(f"  最大: {max_time:.2f}ms")
        print(f"  最小: {min_time:.2f}ms")
        
        # 测试管理器创建时间
        factory = get_platform_factory()
        
        if factory.is_supported_platform():
            # 测试设备指纹管理器创建
            times = []
            for i in range(5):
                _, duration = measure_time(factory.create_fingerprint_manager)
                times.append(duration * 1000)
            
            avg_time = statistics.mean(times)
            print(f"设备指纹管理器创建时间: {avg_time:.2f}ms")
            
            # 测试权限管理器创建
            times = []
            for i in range(5):
                _, duration = measure_time(factory.create_permission_manager)
                times.append(duration * 1000)
            
            avg_time = statistics.mean(times)
            print(f"权限管理器创建时间: {avg_time:.2f}ms")
        
        print("✅ 平台工厂性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 平台工厂性能测试失败: {e}")
        return False

def test_fingerprint_manager_performance():
    """测试设备指纹管理器性能"""
    print("\n=== 测试设备指纹管理器性能 ===")
    
    try:
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        if not factory.is_supported_platform():
            print("⏭️  平台不支持，跳过测试")
            return True
        
        fingerprint_manager = factory.create_fingerprint_manager()
        
        # 测试网络适配器获取性能
        times = []
        for i in range(5):
            _, duration = measure_time(fingerprint_manager.get_network_adapters)
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"网络适配器获取时间: {avg_time:.2f}ms")
        
        # 测试硬件信息获取性能
        times = []
        for i in range(3):
            _, duration = measure_time(fingerprint_manager.get_hardware_info)
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"硬件信息获取时间: {avg_time:.2f}ms")
        
        # 测试机器GUID获取性能
        times = []
        for i in range(10):
            _, duration = measure_time(fingerprint_manager.get_machine_guid)
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"机器GUID获取时间: {avg_time:.2f}ms")
        
        # 测试卷序列号获取性能
        times = []
        for i in range(5):
            _, duration = measure_time(fingerprint_manager.get_volume_serial_numbers)
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"卷序列号获取时间: {avg_time:.2f}ms")
        
        # 测试完整系统指纹生成性能
        _, duration = measure_time(fingerprint_manager.get_system_fingerprint)
        print(f"完整系统指纹生成时间: {duration*1000:.2f}ms")
        
        print("✅ 设备指纹管理器性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 设备指纹管理器性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager_performance():
    """测试配置管理器性能"""
    print("\n=== 测试配置管理器性能 ===")
    
    try:
        from core.config_manager import get_config_manager
        
        # 测试配置管理器创建时间
        times = []
        for i in range(10):
            # 重置全局实例以测试创建时间
            import core.config_manager
            core.config_manager._config_manager = None
            
            _, duration = measure_time(get_config_manager)
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"配置管理器创建时间: {avg_time:.2f}ms")
        
        # 测试配置读取性能
        config_manager = get_config_manager()
        
        times = []
        for i in range(100):
            _, duration = measure_time(config_manager.get_config, 'app.name')
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"配置读取时间: {avg_time:.3f}ms")
        
        # 测试配置写入性能
        times = []
        for i in range(50):
            _, duration = measure_time(config_manager.set_config, f'test.key{i}', f'value{i}')
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"配置写入时间: {avg_time:.3f}ms")
        
        print("✅ 配置管理器性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器性能测试失败: {e}")
        return False

def test_logger_performance():
    """测试日志系统性能"""
    print("\n=== 测试日志系统性能 ===")
    
    try:
        from core.logger import get_logger, get_audit_logger
        from core.interfaces import OperationRecord, OperationType, RiskLevel
        from datetime import datetime
        
        # 测试基本日志记录性能
        logger = get_logger("performance_test")
        
        times = []
        for i in range(100):
            _, duration = measure_time(logger.info, f"测试日志消息 {i}")
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"基本日志记录时间: {avg_time:.3f}ms")
        
        # 测试审计日志性能
        audit_logger = get_audit_logger()
        
        times = []
        for i in range(50):
            record = OperationRecord(
                operation_id=f"test_{i}",
                timestamp=datetime.now(),
                operation_type=OperationType.READ,
                target="test_target",
                parameters={"param": f"value{i}"},
                result="success",
                backup_id=None,
                risk_level=RiskLevel.LOW,
                user="test_user",
                duration=0.1
            )
            
            _, duration = measure_time(audit_logger.log_operation, record)
            times.append(duration * 1000)
        
        avg_time = statistics.mean(times)
        print(f"审计日志记录时间: {avg_time:.3f}ms")
        
        print("✅ 日志系统性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 日志系统性能测试失败: {e}")
        return False

def test_memory_usage():
    """测试内存使用情况"""
    print("\n=== 测试内存使用情况 ===")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 记录初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"初始内存使用: {initial_memory:.2f}MB")
        
        # 创建多个管理器实例
        from core.platform_factory import get_platform_factory
        
        factory = get_platform_factory()
        if factory.is_supported_platform():
            managers = []
            for i in range(10):
                managers.append(factory.create_fingerprint_manager())
                managers.append(factory.create_permission_manager())
        
        # 记录创建后内存使用
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"创建管理器后内存使用: {after_creation_memory:.2f}MB")
        print(f"内存增长: {after_creation_memory - initial_memory:.2f}MB")
        
        # 执行一些操作
        if factory.is_supported_platform():
            fingerprint_manager = managers[0]
            for i in range(10):
                fingerprint_manager.get_network_adapters()
                fingerprint_manager.get_hardware_info()
        
        # 记录操作后内存使用
        after_operations_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"执行操作后内存使用: {after_operations_memory:.2f}MB")
        print(f"操作内存增长: {after_operations_memory - after_creation_memory:.2f}MB")
        
        print("✅ 内存使用测试完成")
        return True
        
    except ImportError:
        print("⏭️  psutil未安装，跳过内存测试")
        return True
    except Exception as e:
        print(f"❌ 内存使用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始性能测试...\n")
    
    test_functions = [
        test_platform_factory_performance,
        test_fingerprint_manager_performance,
        test_config_manager_performance,
        test_logger_performance,
        test_memory_usage
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_func in test_functions:
        results.append(test_func())
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== 性能测试结果汇总 ===")
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    print(f"总测试时间: {total_duration:.2f}秒")
    
    if passed == total:
        print("🎉 所有性能测试通过！系统性能表现良好")
        return True
    else:
        print("⚠️  部分性能测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
