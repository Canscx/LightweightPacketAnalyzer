"""
HTML报告生成器

生成响应式的HTML格式报告，支持：
- 现代化UI设计
- 响应式布局
- 交互式图表
- 浏览器兼容
"""

import os
import logging
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..templates.template_manager import TemplateManager


logger = logging.getLogger(__name__)


class HTMLGenerator:
    """HTML报告生成器"""
    
    def __init__(self, output_dir: Optional[str] = None, 
                 template_dir: Optional[str] = None):
        """
        初始化HTML生成器
        
        Args:
            output_dir: 输出目录
            template_dir: 模板目录
        """
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化模板管理器
        self.template_manager = TemplateManager(template_dir)
        
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, report_data: Dict[str, Any], 
                       output_filename: Optional[str] = None,
                       template_name: str = "report.html") -> str:
        """
        生成完整的HTML报告
        
        Args:
            report_data: 报告数据
            output_filename: 输出文件名
            template_name: 模板文件名
            
        Returns:
            str: 生成的HTML文件路径
        """
        try:
            # 生成文件名
            if output_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"network_analysis_report_{timestamp}.html"
            
            filepath = self.output_dir / output_filename
            
            # 准备模板上下文
            context = self._prepare_template_context(report_data)
            
            # 渲染模板
            if template_name in self.template_manager.list_available_templates():
                html_content = self.template_manager.render_template(template_name, context)
            else:
                # 使用默认模板
                html_content = self._generate_default_template(context)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML报告生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成HTML报告失败: {e}")
            raise
    
    def _prepare_template_context(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """准备模板上下文数据"""
        try:
            context = {
                'report_data': report_data,
                'generation_time': datetime.now(),
                'app_info': {
                    'name': '轻量级数据包分析器',
                    'version': '1.0.0'
                }
            }
            
            # 处理会话信息
            session_info = report_data.get('session_info', {})
            context['session_info'] = session_info
            
            # 处理协议统计
            protocol_stats = report_data.get('protocol_stats', {})
            context['protocol_stats'] = self._format_protocol_stats(protocol_stats)
            
            # 处理流量趋势
            traffic_trends = report_data.get('traffic_trends', {})
            context['traffic_trends'] = self._format_traffic_trends(traffic_trends)
            
            # 处理汇总统计
            summary_stats = report_data.get('summary_stats', {})
            context['summary_stats'] = self._format_summary_stats(summary_stats)
            
            # 处理图表（转换为base64编码）
            context['charts'] = self._process_charts(report_data)
            
            return context
            
        except Exception as e:
            self.logger.error(f"准备模板上下文失败: {e}")
            raise
    
    def _format_protocol_stats(self, protocol_stats: Dict[str, Any]) -> Dict[str, Any]:
        """格式化协议统计数据"""
        try:
            distribution = protocol_stats.get('distribution', {})
            
            # 创建表格数据
            table_data = []
            protocol_counts = distribution.get('protocol_counts', {})
            protocol_bytes = distribution.get('protocol_bytes', {})
            total_packets = distribution.get('total_packets', 1)
            
            for protocol, count in protocol_counts.items():
                bytes_count = protocol_bytes.get(protocol, 0)
                percentage = (count / total_packets) * 100 if total_packets > 0 else 0
                
                table_data.append({
                    'protocol': protocol,
                    'packet_count': count,
                    'byte_count': bytes_count,
                    'percentage': percentage
                })
            
            # 按数据包数量排序
            table_data.sort(key=lambda x: x['packet_count'], reverse=True)
            
            return {
                'distribution': distribution,
                'table_data': table_data,
                'top_protocols': protocol_stats.get('top_protocols_by_count', [])[:10]
            }
            
        except Exception as e:
            self.logger.error(f"格式化协议统计数据失败: {e}")
            return {}
    
    def _format_traffic_trends(self, traffic_trends: Dict[str, Any]) -> Dict[str, Any]:
        """格式化流量趋势数据"""
        try:
            trends_data = traffic_trends.get('trends_data', {})
            peak_info = traffic_trends.get('peak_info', {})
            
            # 格式化时间序列数据
            time_series = traffic_trends.get('time_series', [])
            formatted_series = []
            
            for item in time_series:
                formatted_series.append({
                    'time': datetime.fromtimestamp(item.get('timestamp', 0)).strftime('%H:%M:%S'),
                    'packets': item.get('packet_count', 0),
                    'bytes': item.get('byte_count', 0)
                })
            
            return {
                'trends_data': trends_data,
                'peak_info': peak_info,
                'time_series': formatted_series[:100]  # 限制显示数量
            }
            
        except Exception as e:
            self.logger.error(f"格式化流量趋势数据失败: {e}")
            return {}
    
    def _format_summary_stats(self, summary_stats: Dict[str, Any]) -> Dict[str, Any]:
        """格式化汇总统计数据"""
        try:
            basic_stats = summary_stats.get('basic_stats', {})
            advanced_stats = summary_stats.get('advanced_stats', {})
            
            # 创建关键指标
            key_metrics = [
                {
                    'name': '总数据包数',
                    'value': f"{advanced_stats.get('total_packets', 0):,}",
                    'icon': '📦'
                },
                {
                    'name': '总字节数',
                    'value': self._format_bytes(advanced_stats.get('total_bytes', 0)),
                    'icon': '💾'
                },
                {
                    'name': '协议类型',
                    'value': f"{advanced_stats.get('protocol_diversity', 0)} 种",
                    'icon': '🔗'
                },
                {
                    'name': '平均速率',
                    'value': f"{advanced_stats.get('avg_packet_rate', 0):.1f} 包/秒",
                    'icon': '⚡'
                }
            ]
            
            return {
                'basic_stats': basic_stats,
                'advanced_stats': advanced_stats,
                'key_metrics': key_metrics
            }
            
        except Exception as e:
            self.logger.error(f"格式化汇总统计数据失败: {e}")
            return {}
    
    def _process_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """处理图表，转换为base64编码"""
        charts = {}
        
        try:
            # 处理各种图表
            chart_keys = [
                'protocol_pie_chart',
                'traffic_trend_chart', 
                'top_protocols_chart',
                'packet_size_histogram'
            ]
            
            for key in chart_keys:
                if key in report_data:
                    chart_path = report_data[key]
                    if os.path.exists(chart_path):
                        charts[key] = self._image_to_base64(chart_path)
            
            return charts
            
        except Exception as e:
            self.logger.error(f"处理图表失败: {e}")
            return {}
    
    def _image_to_base64(self, image_path: str) -> str:
        """将图片转换为base64编码"""
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                base64_data = base64.b64encode(img_data).decode('utf-8')
                
                # 确定MIME类型
                ext = Path(image_path).suffix.lower()
                mime_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif'
                }.get(ext, 'image/png')
                
                return f"data:{mime_type};base64,{base64_data}"
                
        except Exception as e:
            self.logger.error(f"图片转base64失败: {e}")
            return ""
    
    def _format_bytes(self, bytes_count: int) -> str:
        """格式化字节数"""
        if bytes_count < 1024:
            return f"{bytes_count} B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count / 1024:.1f} KB"
        elif bytes_count < 1024 * 1024 * 1024:
            return f"{bytes_count / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_count / (1024 * 1024 * 1024):.1f} GB"
    
    def _generate_default_template(self, context: Dict[str, Any]) -> str:
        """生成默认HTML模板"""
        try:
            session_info = context.get('session_info', {})
            protocol_stats = context.get('protocol_stats', {})
            traffic_trends = context.get('traffic_trends', {})
            summary_stats = context.get('summary_stats', {})
            charts = context.get('charts', {})
            generation_time = context.get('generation_time', datetime.now())
            
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网络分析报告 - {session_info.get('name', '未知会话')}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #007acc, #0056b3);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header .meta {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fafafa;
        }}
        .section h2 {{
            color: #007acc;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-card .icon {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .metric-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #007acc;
        }}
        .metric-card .name {{
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stats-table th {{
            background: #007acc;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
        }}
        .stats-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        .stats-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .stats-table tr:hover {{
            background-color: #f0f8ff;
        }}
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
            }}
            .content {{
                padding: 15px;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>网络流量分析报告</h1>
            <div class="meta">
                <p>会话: {session_info.get('name', '未知会话')} | 生成时间: {generation_time.strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            </div>
        </header>
        
        <div class="content">
            <!-- 关键指标 -->
            <div class="section">
                <h2>📊 关键指标</h2>
                <div class="metrics-grid">
            """
            
            # 添加关键指标卡片
            key_metrics = summary_stats.get('key_metrics', [])
            for metric in key_metrics:
                html_content += f"""
                    <div class="metric-card">
                        <div class="icon">{metric.get('icon', '📈')}</div>
                        <div class="value">{metric.get('value', 'N/A')}</div>
                        <div class="name">{metric.get('name', '')}</div>
                    </div>
                """
            
            html_content += """
                </div>
            </div>
            
            <!-- 会话信息 -->
            <div class="section">
                <h2>ℹ️ 会话信息</h2>
                <div class="table-container">
                    <table class="stats-table">
                        <tr><th>项目</th><th>值</th></tr>
            """
            
            # 添加会话信息表格
            session_items = [
                ('会话ID', session_info.get('session_id', 'N/A')),
                ('会话名称', session_info.get('name', 'N/A')),
                ('创建时间', session_info.get('created_time', 'N/A')),
                ('数据包数量', f"{session_info.get('packet_count', 0):,}"),
                ('持续时间', f"{session_info.get('duration', 0):.2f} 秒"),
            ]
            
            for name, value in session_items:
                html_content += f"<tr><td>{name}</td><td>{value}</td></tr>"
            
            html_content += """
                    </table>
                </div>
            </div>
            
            <!-- 协议统计 -->
            <div class="section">
                <h2>🔗 协议统计分析</h2>
            """
            
            # 添加协议饼图
            if 'protocol_pie_chart' in charts:
                html_content += f"""
                <div class="chart-container">
                    <img src="{charts['protocol_pie_chart']}" alt="协议分布图">
                </div>
                """
            
            # 添加协议统计表格
            protocol_table_data = protocol_stats.get('table_data', [])
            if protocol_table_data:
                html_content += """
                <div class="table-container">
                    <table class="stats-table">
                        <tr>
                            <th>协议类型</th>
                            <th>数据包数量</th>
                            <th>字节数</th>
                            <th>占比</th>
                        </tr>
                """
                
                for row in protocol_table_data[:15]:  # 显示前15个
                    html_content += f"""
                        <tr>
                            <td>{row['protocol']}</td>
                            <td>{row['packet_count']:,}</td>
                            <td>{self._format_bytes(row['byte_count'])}</td>
                            <td>{row['percentage']:.2f}%</td>
                        </tr>
                    """
                
                html_content += "</table></div>"
            
            html_content += """
            </div>
            
            <!-- 流量趋势 -->
            <div class="section">
                <h2>📈 流量趋势分析</h2>
            """
            
            # 添加流量趋势图
            if 'traffic_trend_chart' in charts:
                html_content += f"""
                <div class="chart-container">
                    <img src="{charts['traffic_trend_chart']}" alt="流量趋势图">
                </div>
                """
            
            # 添加峰值信息
            peak_info = traffic_trends.get('peak_info', {})
            if peak_info:
                html_content += f"""
                <div style="background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="color: #007acc; margin-top: 0;">流量峰值信息</h4>
                    <p><strong>峰值流量:</strong> {peak_info.get('max_packets', 0)} 个数据包</p>
                    <p><strong>峰值时间:</strong> {peak_info.get('peak_time', 'N/A')}</p>
                    <p><strong>平均流量:</strong> {peak_info.get('avg_packets', 0):.1f} 个数据包/秒</p>
                </div>
                """
            
            html_content += """
            </div>
        </div>
        
        <footer class="footer">
            <p>由轻量级数据包分析器生成 | © 2024</p>
        </footer>
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"生成默认模板失败: {e}")
            raise
    
    def create_interactive_chart_html(self, chart_data: Dict[str, Any]) -> str:
        """
        创建交互式图表HTML
        
        Args:
            chart_data: 图表数据
            
        Returns:
            str: 包含交互式图表的HTML代码
        """
        try:
            # 这里可以集成Chart.js或其他JavaScript图表库
            # 暂时返回静态图表的HTML
            html = """
            <div class="interactive-chart">
                <canvas id="protocolChart" width="400" height="200"></canvas>
                <script>
                    // 这里可以添加Chart.js或其他图表库的代码
                    console.log('Interactive chart placeholder');
                </script>
            </div>
            """
            return html
            
        except Exception as e:
            self.logger.error(f"创建交互式图表失败: {e}")
            return ""
    
    def copy_static_files(self):
        """复制静态文件（CSS、JS等）"""
        try:
            # 创建静态文件目录
            static_dir = self.output_dir / "static"
            static_dir.mkdir(exist_ok=True)
            
            # 复制CSS文件
            css_dir = static_dir / "css"
            css_dir.mkdir(exist_ok=True)
            
            # 这里可以复制模板目录中的CSS文件
            # 暂时跳过，因为我们使用内联样式
            
        except Exception as e:
            self.logger.error(f"复制静态文件失败: {e}")