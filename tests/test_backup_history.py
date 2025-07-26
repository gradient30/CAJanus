#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份历史加载功能测试脚本
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager

def test_backup_history_loading():
    """测试备份历史加载功能"""
    print("=== 备份历史加载功能测试 ===")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 测试1: 检查备份目录
    print("\n1. 检查备份目录:")
    backup_dir = config_manager.get_backup_directory()
    print(f"  备份目录: {backup_dir}")
    print(f"  目录存在: {backup_dir.exists()}")
    
    if backup_dir.exists():
        files = list(backup_dir.iterdir())
        print(f"  目录中的文件数量: {len(files)}")
        for file in files:
            print(f"    {file.name} ({'文件' if file.is_file() else '目录'})")
    
    # 测试2: 模拟备份历史加载逻辑
    print("\n2. 模拟备份历史加载:")
    
    def format_file_size(size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    backup_history = []
    
    try:
        if not os.path.exists(backup_dir):
            print(f"  ⚠️  备份目录不存在: {backup_dir}")
        else:
            print(f"  ✅ 备份目录存在，开始扫描...")
            
            # 扫描备份文件
            all_files = os.listdir(backup_dir)
            print(f"  目录中所有文件: {all_files}")
            
            backup_files = [f for f in all_files if f.endswith('.bak') and f.startswith('backup_')]
            print(f"  找到的备份文件: {backup_files}")
            
            for filename in backup_files:
                file_path = os.path.join(backup_dir, filename)
                print(f"\n  处理文件: {filename}")
                
                try:
                    # 获取文件信息
                    file_stat = os.stat(file_path)
                    file_size = format_file_size(file_stat.st_size)
                    print(f"    文件大小: {file_size}")
                    
                    # 尝试从备份文件中读取时间戳
                    backup_time = None
                    backup_type = "完整备份"
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                            print(f"    成功读取JSON数据")
                            
                            # 优先使用可读时间戳
                            if 'timestamp_readable' in backup_data:
                                backup_time = backup_data['timestamp_readable']
                                print(f"    使用可读时间戳: {backup_time}")
                            elif 'timestamp' in backup_data:
                                # 如果是ISO格式，转换为可读格式
                                try:
                                    dt = datetime.fromisoformat(backup_data['timestamp'].replace('Z', '+00:00'))
                                    backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    print(f"    从ISO时间戳转换: {backup_time}")
                                except:
                                    backup_time = backup_data['timestamp']
                                    print(f"    使用原始时间戳: {backup_time}")
                            
                            backup_type = backup_data.get('backup_type', '完整备份')
                            print(f"    备份类型: {backup_type}")
                            
                    except (json.JSONDecodeError, KeyError, Exception) as e:
                        print(f"    JSON读取失败: {e}")
                        # 如果无法读取备份文件，从文件名解析时间
                        try:
                            # 从文件名提取时间戳 backup_20240115_143025.bak
                            time_part = filename.replace('backup_', '').replace('.bak', '')
                            dt = datetime.strptime(time_part, '%Y%m%d_%H%M%S')
                            backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"    从文件名解析时间: {backup_time}")
                        except ValueError as ve:
                            print(f"    文件名解析失败: {ve}")
                            # 使用文件修改时间
                            dt = datetime.fromtimestamp(file_stat.st_mtime)
                            backup_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"    使用文件修改时间: {backup_time}")
                    
                    backup_info = {
                        "time": backup_time or "未知时间",
                        "type": backup_type,
                        "size": file_size,
                        "status": "正常",
                        "file": filename,
                        "path": file_path
                    }
                    
                    backup_history.append(backup_info)
                    print(f"    ✅ 成功处理: {backup_info}")
                    
                except Exception as e:
                    print(f"    ❌ 处理文件失败: {e}")
                    continue
            
            # 按时间排序（最新的在前）
            backup_history.sort(key=lambda x: x["time"], reverse=True)
            print(f"\n  排序后的备份历史:")
            for i, backup in enumerate(backup_history):
                print(f"    {i+1}. {backup['time']} - {backup['type']} - {backup['size']}")
    
    except Exception as e:
        print(f"  ❌ 加载备份历史失败: {e}")
        backup_history = []
    
    # 测试3: 检查具体的备份文件内容
    print("\n3. 检查具体备份文件内容:")
    
    if backup_dir.exists():
        for file_path in backup_dir.glob("backup_*.bak"):
            print(f"\n  检查文件: {file_path.name}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"    文件大小: {len(content)} 字符")
                    
                    # 尝试解析JSON
                    try:
                        data = json.loads(content)
                        print(f"    JSON解析成功")
                        print(f"    包含的键: {list(data.keys())}")
                        
                        if 'timestamp' in data:
                            print(f"    timestamp: {data['timestamp']}")
                        if 'timestamp_readable' in data:
                            print(f"    timestamp_readable: {data['timestamp_readable']}")
                        if 'backup_type' in data:
                            print(f"    backup_type: {data['backup_type']}")
                            
                    except json.JSONDecodeError as e:
                        print(f"    JSON解析失败: {e}")
                        print(f"    文件前100字符: {content[:100]}")
                        
            except Exception as e:
                print(f"    读取文件失败: {e}")
    
    print(f"\n=== 测试完成，找到 {len(backup_history)} 个有效备份 ===")
    
    return backup_history

if __name__ == "__main__":
    test_backup_history_loading()
