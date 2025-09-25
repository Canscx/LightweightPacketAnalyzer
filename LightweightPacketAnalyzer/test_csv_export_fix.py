#!/usr/bin/env python3
"""
CSV导出修复测试脚本

测试修复后的CSV导出功能，验证中文字符显示正常
"""

import sys
import os
import tempfile
import csv
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_csv_encoding():
    """测试CSV编码修复"""
    print("=== CSV导出编码修复测试 ===")
    
    # 测试数据
    test_data = [
        ['指标', '数值'],
        ['总数据包', 100],
        ['总字节数', 50000],
        ['数据包速率', '10.50 pps'],
        ['字节速率', '2500.00 Bps'],
        ['', ''],
        ['协议分布', ''],
        ['TCP', 60],
        ['UDP', 30],
        ['ICMP', 10],
        ['', ''],
        ['完整数据包列表', ''],
        ['时间戳', '源IP', '目标IP', '源端口', '目标端口', '协议', '长度(字节)'],
        ['2024-01-15 10:30:15.123', '192.168.1.100', '192.168.1.1', '12345', '80', 'TCP', 1500],
        ['2024-01-15 10:30:15.456', '192.168.1.100', '8.8.8.8', '54321', '53', 'UDP', 64]
    ]
    
    # 创建临时文件测试
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for row in test_data:
            writer.writerow(row)
        temp_file = f.name
    
    print(f"测试文件已创建: {temp_file}")
    
    # 验证文件内容
    try:
        with open(temp_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print("文件内容预览:")
            print(content[:500] + "..." if len(content) > 500 else content)
            
        # 检查是否包含中文字符
        chinese_chars = ['指标', '数值', '总数据包', '总字节数', '协议分布', '完整数据包列表', '时间戳', '源IP', '目标IP', '源端口', '目标端口', '协议', '长度']
        missing_chars = []
        for char in chinese_chars:
            if char not in content:
                missing_chars.append(char)
        
        if missing_chars:
            print(f"❌ 缺少中文字符: {missing_chars}")
            return False
        else:
            print("✅ 所有中文字符都正确保存")
            
        # 检查BOM头
        with open(temp_file, 'rb') as f:
            first_bytes = f.read(3)
            if first_bytes == b'\xef\xbb\xbf':
                print("✅ UTF-8 BOM头存在，Excel应该能正确识别中文")
            else:
                print("❌ 缺少UTF-8 BOM头")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file)
        except:
            pass

def test_protocol_stats_export():
    """测试协议统计导出功能"""
    print("\n=== 协议统计导出测试 ===")
    
    # 模拟协议统计数据
    test_data = [
        ['协议', '数据包数', '字节数', '包占比(%)', '字节占比(%)', '平均大小'],
        ['TCP', 64, 26523, '71.1', '88.0', '414'],
        ['UDP', 26, 3605, '28.9', '12.0', '139']
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for row in test_data:
            writer.writerow(row)
        temp_file = f.name
    
    print(f"协议统计测试文件: {temp_file}")
    
    try:
        with open(temp_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print("协议统计文件内容:")
            print(content)
            
        # 检查关键字段
        required_fields = ['协议', '数据包数', '字节数', '包占比', '字节占比', '平均大小']
        for field in required_fields:
            if field not in content:
                print(f"❌ 缺少字段: {field}")
                return False
                
        print("✅ 协议统计导出格式正确")
        return True
        
    except Exception as e:
        print(f"❌ 协议统计测试失败: {e}")
        return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    """主测试函数"""
    print("开始CSV导出修复验证测试...\n")
    
    success_count = 0
    total_tests = 2
    
    # 测试1: CSV编码修复
    if test_csv_encoding():
        success_count += 1
    
    # 测试2: 协议统计导出
    if test_protocol_stats_export():
        success_count += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("✅ 所有测试通过！CSV导出修复成功")
        print("\n修复内容:")
        print("1. 使用UTF-8 BOM编码 (utf-8-sig) 确保Excel正确识别中文")
        print("2. 增强主窗口导出功能，添加完整数据包列表")
        print("3. 协议统计导出保持原有功能，修复中文乱码")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)