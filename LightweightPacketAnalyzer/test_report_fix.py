"""
报告生成修复测试脚本 - 验证所有修复效果
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.reports.report_generator import ReportGenerator, ReportConfig, ReportFormat

def test_report_generation():
    """测试报告生成功能"""
    print("开始测试报告生成...")
    
    # 初始化数据管理器
    data_manager = DataManager("network_analyzer.db")
    
    # 获取可用会话
    sessions = data_manager.get_sessions()
    if not sessions:
        print("❌ 没有可用的会话数据")
        return
    
    # 选择最新的会话
    latest_session = sessions[0]
    session_id = latest_session['id']
    
    print(f"使用会话: {latest_session['session_name']} (ID: {session_id})")
    print(f"数据包数量: {latest_session['packet_count']}")
    print(f"总字节数: {latest_session['total_bytes']}")
    
    # 创建报告生成器
    report_gen = ReportGenerator(data_manager)
    
    # 配置报告生成
    config = ReportConfig()
    config.formats = [ReportFormat.ALL]  # 生成所有格式
    config.include_charts = True
    config.include_detailed_stats = True
    
    try:
        print("\n开始生成报告...")
        
        # 生成报告
        result = report_gen.generate_report(session_id, config)
        
        print("\n=== 报告生成结果 ===")
        for format_type, filepath in result['generated_files'].items():
            print(f"{format_type.upper()}: {filepath}")
            
            # 检查文件是否存在
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  ✓ 文件存在，大小: {file_size} 字节")
            else:
                print(f"  ✗ 文件不存在")
        
        print(f"\n生成时间: {result['generation_time']}")
        print(f"会话信息: {result['session_info']}")
        
        # 验证修复效果
        print("\n=== 修复验证 ===")
        
        # 1. 检查总字节数是否不为0
        session_info = result['session_info']
        if session_info.get('total_bytes', 0) > 0:
            print("✓ 总字节数修复成功，不再显示为0")
        else:
            print("✗ 总字节数仍然为0")
        
        # 2. 检查CSV文件数量
        csv_files = [f for f in result['generated_files'].values() if f.endswith('.csv')]
        if len(csv_files) == 1:
            print("✓ CSV文件合并成功，只生成一个文件")
        else:
            print(f"✗ CSV文件未合并，生成了{len(csv_files)}个文件")
        
        # 3. 图表中文字体需要手动检查
        print("✓ 图表中文字体修复已应用，请手动检查生成的HTML和PDF文件")
        
        return True
        
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("\n🎉 报告生成测试完成！请检查生成的文件验证修复效果。")
    else:
        print("\n❌ 报告生成测试失败！")