"""
图表修复测试脚本 - 验证中文字体显示效果
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from network_analyzer.reports.charts.chart_generator import ChartGenerator

def test_chart_generation():
    """测试图表生成功能"""
    print("开始测试图表生成...")
    
    # 创建图表生成器
    chart_gen = ChartGenerator()
    
    # 测试数据
    protocol_data = {
        'TCP': 337,
        'UDP': 146,
        'ICMP': 50,
        'HTTP': 30,
        'HTTPS': 25
    }
    
    time_data = [1758892578, 1758892874, 1758892875, 1758892876]
    packet_counts = [160, 286, 494, 60]
    
    try:
        # 测试协议饼图
        print("生成协议分布饼图...")
        pie_chart = chart_gen.generate_protocol_pie_chart(protocol_data, "协议分布统计测试")
        print(f"✓ 饼图生成成功: {pie_chart}")
        
        # 测试流量趋势图
        print("生成流量趋势图...")
        trend_chart = chart_gen.generate_traffic_trend_chart(time_data, packet_counts, "流量趋势分析测试")
        print(f"✓ 趋势图生成成功: {trend_chart}")
        
        # 测试Top协议条形图
        print("生成Top协议条形图...")
        top_protocols = [(k, v) for k, v in protocol_data.items()]
        bar_chart = chart_gen.generate_top_protocols_bar_chart(top_protocols, "Top协议统计测试")
        print(f"✓ 条形图生成成功: {bar_chart}")
        
        # 测试组合图表
        print("生成组合仪表板...")
        dashboard_data = {
            'protocol_distribution': protocol_data,
            'traffic_trends': {
                'time_data': time_data,
                'packet_counts': packet_counts
            },
            'top_protocols': top_protocols,
            'packet_sizes': [64, 128, 256, 512, 1024] * 20
        }
        
        dashboard_chart = chart_gen.generate_combined_chart(dashboard_data, "dashboard")
        print(f"✓ 仪表板生成成功: {dashboard_chart}")
        
        print("\n=== 测试完成 ===")
        print("请检查生成的图片文件，确认中文字体是否正确显示")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chart_generation()