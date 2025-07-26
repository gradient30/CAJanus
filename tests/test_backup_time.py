#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份功能时间处理测试脚本
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager

def test_backup_time_handling():
    """测试备份功能的时间处理"""
    print("=== 备份功能时间处理测试 ===")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 测试1: 检查备份目录
    print("\n1. 检查备份目录:")
    backup_dir = config_manager.get_backup_directory()
    print(f"  备份目录: {backup_dir}")
    print(f"  目录存在: {backup_dir.exists()}")
    
    # 测试2: 创建测试备份文件
    print("\n2. 创建测试备份文件:")
    current_time = datetime.now()
    timestamp_for_filename = current_time.strftime("%Y%m%d_%H%M%S")
    timestamp_iso = current_time.isoformat()
    timestamp_readable = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"  当前时间: {current_time}")
    print(f"  文件名时间戳: {timestamp_for_filename}")
    print(f"  ISO时间戳: {timestamp_iso}")
    print(f"  可读时间戳: {timestamp_readable}")
    
    # 创建测试备份数据
    test_backup_data = {
        "timestamp": timestamp_iso,
        "timestamp_readable": timestamp_readable,
        "backup_type": "完整备份",
        "system_info": {
            "os_name": "Windows",
            "os_version": "10",
            "architecture": "AMD64",
            "python_version": "3.9.0"
        },
        "registry_data": {},
        "network_config": {
            "adapters": []
        },
        "hardware_info": {
            "machine_guid": "test-guid",
            "volume_serials": [],
            "hardware_details": {}
        }
    }
    
    # 保存测试备份文件
    test_backup_filename = f"backup_{timestamp_for_filename}.bak"
    test_backup_path = backup_dir / test_backup_filename
    
    try:
        with open(test_backup_path, 'w', encoding='utf-8') as f:
            json.dump(test_backup_data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ 测试备份文件已创建: {test_backup_filename}")
    except Exception as e:
        print(f"  ❌ 创建测试备份文件失败: {e}")
        return
    
    # 测试3: 验证时间戳解析
    print("\n3. 验证时间戳解析:")
    
    # 测试从文件读取时间戳
    try:
        with open(test_backup_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        loaded_timestamp = loaded_data.get('timestamp')
        loaded_readable = loaded_data.get('timestamp_readable')
        
        print(f"  从文件读取的ISO时间戳: {loaded_timestamp}")
        print(f"  从文件读取的可读时间戳: {loaded_readable}")
        
        # 验证ISO时间戳解析
        if loaded_timestamp:
            try:
                parsed_dt = datetime.fromisoformat(loaded_timestamp.replace('Z', '+00:00'))
                formatted_time = parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
                print(f"  ISO时间戳解析结果: {formatted_time}")
                print(f"  ✅ ISO时间戳解析成功")
            except Exception as e:
                print(f"  ❌ ISO时间戳解析失败: {e}")
        
        # 验证可读时间戳
        if loaded_readable:
            print(f"  ✅ 可读时间戳正常: {loaded_readable}")
        
    except Exception as e:
        print(f"  ❌ 读取备份文件失败: {e}")
    
    # 测试4: 测试文件名时间戳解析
    print("\n4. 测试文件名时间戳解析:")
    try:
        # 从文件名提取时间戳
        time_part = test_backup_filename.replace('backup_', '').replace('.bak', '')
        dt = datetime.strptime(time_part, '%Y%m%d_%H%M%S')
        filename_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  从文件名解析的时间: {filename_time}")
        print(f"  ✅ 文件名时间戳解析成功")
    except Exception as e:
        print(f"  ❌ 文件名时间戳解析失败: {e}")
    
    # 测试5: 测试文件大小格式化
    print("\n5. 测试文件大小格式化:")
    try:
        file_stat = os.stat(test_backup_path)
        file_size_bytes = file_stat.st_size
        
        # 实现文件大小格式化
        def format_file_size(size_bytes):
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_names[i]}"
        
        formatted_size = format_file_size(file_size_bytes)
        print(f"  文件大小(字节): {file_size_bytes}")
        print(f"  格式化文件大小: {formatted_size}")
        print(f"  ✅ 文件大小格式化成功")
    except Exception as e:
        print(f"  ❌ 文件大小格式化失败: {e}")
    
    # 测试6: 模拟备份历史加载
    print("\n6. 模拟备份历史加载:")
    try:
        backup_history = []
        
        # 扫描备份目录
        for filename in os.listdir(backup_dir):
            if filename.endswith('.bak') and filename.startswith('backup_'):
                file_path = backup_dir / filename
                
                # 获取文件信息
                file_stat = os.stat(file_path)
                file_size = format_file_size(file_stat.st_size)
                
                # 读取备份数据
                backup_time = None
                backup_type = "完整备份"
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                        
                        if 'timestamp_readable' in backup_data:
                            backup_time = backup_data['timestamp_readable']
                        elif 'timestamp' in backup_data:
                            try:
                                dt = datetime.fromisoformat(backup_data['timestamp'].replace('Z', '+00:00'))
                                backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                backup_time = backup_data['timestamp']
                        
                        backup_type = backup_data.get('backup_type', '完整备份')
                        
                except Exception:
                    # 从文件名解析时间
                    try:
                        time_part = filename.replace('backup_', '').replace('.bak', '')
                        dt = datetime.strptime(time_part, '%Y%m%d_%H%M%S')
                        backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        dt = datetime.fromtimestamp(file_stat.st_mtime)
                        backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                
                backup_history.append({
                    "time": backup_time or "未知时间",
                    "type": backup_type,
                    "size": file_size,
                    "status": "正常",
                    "file": filename
                })
        
        # 按时间排序
        backup_history.sort(key=lambda x: x["time"], reverse=True)
        
        print(f"  找到 {len(backup_history)} 个备份文件:")
        for backup in backup_history:
            print(f"    {backup['time']} - {backup['type']} - {backup['size']} - {backup['file']}")
        
        print(f"  ✅ 备份历史加载成功")
        
    except Exception as e:
        print(f"  ❌ 备份历史加载失败: {e}")
    
    # 清理测试文件
    print("\n7. 清理测试文件:")
    try:
        if test_backup_path.exists():
            os.remove(test_backup_path)
            print(f"  ✅ 已删除测试文件: {test_backup_filename}")
    except Exception as e:
        print(f"  ⚠️  删除测试文件失败: {e}")
    
    print("\n=== 备份功能时间处理测试完成 ===")

if __name__ == "__main__":
    test_backup_time_handling()
