#!/usr/bin/env python3
"""
报告生成功能测试脚本

测试报告生成功能的各个组件是否正常工作
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.reports.report_generator import ReportGenerator, ReportConfig, ReportFormat


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_report_generation():
    """测试报告生成功能"""
    print("=== 报告生成功能测试 ===")
    
    try:
        # 初始化数据管理器
        db_path = "test_traffic_trends.db"  # 使用有数据的数据库
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        data_manager = DataManager(db_path)
        print("✅ 数据管理器初始化成功")
        
        # 初始化报告生成器
        report_generator = ReportGenerator(data_manager)
        print("✅ 报告生成器初始化成功")
        
        # 获取可用会话
        sessions = report_generator.get_available_sessions()
        print(f"✅ 找到 {len(sessions)} 个可用会话")
        
        if not sessions:
            print("❌ 没有可用的会话数据")
            return False
        
        # 选择第一个会话进行测试
        test_session = sessions[0]
        session_id = test_session.get('id')
        print(f"📋 测试会话: {session_id} - {test_session.get('name', 'N/A')}")
        
        # 验证会话数据
        if not report_generator.validate_session(session_id):
            print(f"❌ 会话 {session_id} 数据无效")
            return False
        
        print("✅ 会话数据验证通过")
        
        # 获取报告预览
        preview = report_generator.get_report_preview(session_id)
        if preview.get('valid'):
            print(f"✅ 报告预览: {preview.get('packet_count', 0)} 个数据包")
        else:
            print(f"❌ 报告预览失败: {preview.get('error', '未知错误')}")
            return False
        
        # 测试生成流水线
        print("🔧 测试生成流水线...")
        test_results = report_generator.test_generation_pipeline(session_id)
        
        for component, success in test_results.items():
            status = "✅" if success else "❌"
            print(f"{status} {component}: {'通过' if success else '失败'}")
        
        if not test_results.get('overall', False):
            print("❌ 生成流水线测试失败")
            return False
        
        print("✅ 生成流水线测试通过")
        
        # 测试实际报告生成（仅HTML格式，速度较快）
        print("📄 生成测试报告...")
        config = ReportConfig()
        config.formats = [ReportFormat.HTML]
        config.include_charts = True
        
        result = report_generator.generate_report(session_id, config)
        
        if result.get('success'):
            generated_files = result.get('generated_files', {})
            print(f"✅ 报告生成成功，生成了 {len(generated_files)} 个文件:")
            for file_type, file_path in generated_files.items():
                print(f"   • {file_type}: {Path(file_path).name}")
            return True
        else:
            print("❌ 报告生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        logging.exception("测试报告生成功能时出现异常")
        return False


def main():
    """主函数"""
    setup_logging()
    
    print("开始测试报告生成功能...")
    print("-" * 50)
    
    success = test_report_generation()
    
    print("-" * 50)
    if success:
        print("🎉 报告生成功能测试通过！")
    else:
        print("💥 报告生成功能测试失败！")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())