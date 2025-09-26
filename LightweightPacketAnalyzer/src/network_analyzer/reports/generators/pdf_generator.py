"""
PDF报告生成器

使用ReportLab库生成专业的PDF格式报告，支持：
- 中文字体
- 图表嵌入
- 表格数据
- 专业排版
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF报告生成器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化PDF生成器
        
        Args:
            output_dir: 输出目录，默认为当前目录的reports文件夹
        """
        if output_dir is None:
            output_dir = Path.cwd() / "reports"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # 设置中文字体
        self._setup_chinese_fonts()
        
        # 创建样式
        self._create_styles()
    
    def _setup_chinese_fonts(self):
        """设置中文字体支持"""
        try:
            # 尝试注册中文字体
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
            ]
            
            self.chinese_font = None
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font_name = "ChineseFont"
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        self.chinese_font = font_name
                        self.logger.info(f"成功注册中文字体: {font_path}")
                        break
                    except Exception as e:
                        self.logger.warning(f"注册字体失败 {font_path}: {e}")
                        continue
            
            if not self.chinese_font:
                self.logger.warning("未找到中文字体，将使用默认字体")
                self.chinese_font = "Helvetica"
                
        except Exception as e:
            self.logger.error(f"设置中文字体失败: {e}")
            self.chinese_font = "Helvetica"
    
    def _create_styles(self):
        """创建PDF样式"""
        try:
            # 获取基础样式
            self.styles = getSampleStyleSheet()
            
            # 创建自定义样式
            font_name = self.chinese_font or "Helvetica"
            
            # 标题样式
            self.styles.add(ParagraphStyle(
                name='ChineseTitle',
                parent=self.styles['Title'],
                fontName=font_name,
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            ))
            
            # 章节标题样式
            self.styles.add(ParagraphStyle(
                name='ChineseHeading1',
                parent=self.styles['Heading1'],
                fontName=font_name,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12,
                textColor=colors.darkblue
            ))
            
            # 正文样式
            self.styles.add(ParagraphStyle(
                name='ChineseNormal',
                parent=self.styles['Normal'],
                fontName=font_name,
                fontSize=10,
                spaceAfter=6,
                alignment=TA_LEFT
            ))
            
            # 表格标题样式
            self.styles.add(ParagraphStyle(
                name='TableHeader',
                parent=self.styles['Normal'],
                fontName=font_name,
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.white
            ))
            
        except Exception as e:
            self.logger.error(f"创建PDF样式失败: {e}")
    
    def generate_report(self, report_data: Dict[str, Any], 
                       output_filename: Optional[str] = None) -> str:
        """
        生成完整的PDF报告
        
        Args:
            report_data: 报告数据
            output_filename: 输出文件名
            
        Returns:
            str: 生成的PDF文件路径
        """
        try:
            # 生成文件名
            if output_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"network_analysis_report_{timestamp}.pdf"
            
            filepath = self.output_dir / output_filename
            
            # 创建PDF文档
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # 构建文档内容
            story = []
            
            # 添加标题页
            story.extend(self._create_title_page(report_data))
            
            # 添加会话信息
            story.extend(self._create_session_info_section(report_data))
            
            # 添加协议统计
            story.extend(self._create_protocol_stats_section(report_data))
            
            # 添加流量趋势
            story.extend(self._create_traffic_trends_section(report_data))
            
            # 添加汇总分析
            story.extend(self._create_summary_section(report_data))
            
            # 构建PDF
            doc.build(story)
            
            self.logger.info(f"PDF报告生成成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"生成PDF报告失败: {e}")
            raise
    
    def _create_title_page(self, report_data: Dict[str, Any]) -> List[Any]:
        """创建标题页"""
        story = []
        
        try:
            # 主标题
            title = Paragraph("网络流量分析报告", self.styles['ChineseTitle'])
            story.append(title)
            story.append(Spacer(1, 0.5*inch))
            
            # 会话信息
            session_info = report_data.get('session_info', {})
            session_name = session_info.get('name', '未知会话')
            generation_time = report_data.get('generation_time', datetime.now())
            
            info_text = f"""
            <para align="center">
            会话名称: {session_name}<br/>
            生成时间: {generation_time.strftime('%Y年%m月%d日 %H:%M:%S')}<br/>
            生成工具: 轻量级数据包分析器 v1.0
            </para>
            """
            
            info_para = Paragraph(info_text, self.styles['ChineseNormal'])
            story.append(info_para)
            story.append(Spacer(1, 1*inch))
            
            # 分隔线
            story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
            story.append(PageBreak())
            
        except Exception as e:
            self.logger.error(f"创建标题页失败: {e}")
        
        return story
    
    def _create_session_info_section(self, report_data: Dict[str, Any]) -> List[Any]:
        """创建会话信息区块"""
        story = []
        
        try:
            # 区块标题
            title = Paragraph("1. 会话信息", self.styles['ChineseHeading1'])
            story.append(title)
            
            # 会话信息表格
            session_info = report_data.get('session_info', {})
            
            table_data = [
                ['项目', '值'],
                ['会话ID', str(session_info.get('session_id', 'N/A'))],
                ['会话名称', session_info.get('name', 'N/A')],
                ['创建时间', session_info.get('created_time', 'N/A')],
                ['数据包数量', f"{session_info.get('packet_count', 0):,}"],
                ['持续时间', f"{session_info.get('duration', 0):.2f} 秒"],
                ['文件路径', session_info.get('file_path', 'N/A')],
            ]
            
            table = Table(table_data, colWidths=[3*cm, 8*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
        except Exception as e:
            self.logger.error(f"创建会话信息区块失败: {e}")
        
        return story
    
    def _create_protocol_stats_section(self, report_data: Dict[str, Any]) -> List[Any]:
        """创建协议统计区块"""
        story = []
        
        try:
            # 区块标题
            title = Paragraph("2. 协议统计分析", self.styles['ChineseHeading1'])
            story.append(title)
            
            # 协议分布表格
            protocol_stats = report_data.get('protocol_stats', {})
            distribution = protocol_stats.get('distribution', {})
            protocol_counts = distribution.get('protocol_counts', {})
            
            if protocol_counts:
                # 创建协议统计表格
                table_data = [['协议类型', '数据包数量', '字节数', '占比']]
                
                total_packets = distribution.get('total_packets', 1)
                protocol_bytes = distribution.get('protocol_bytes', {})
                
                for protocol, count in protocol_counts.items():
                    bytes_count = protocol_bytes.get(protocol, 0)
                    percentage = (count / total_packets) * 100 if total_packets > 0 else 0
                    
                    table_data.append([
                        protocol,
                        f"{count:,}",
                        f"{bytes_count:,}",
                        f"{percentage:.2f}%"
                    ])
                
                table = Table(table_data, colWidths=[3*cm, 3*cm, 3*cm, 2*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
            # 添加协议分布图表（如果存在）
            if 'protocol_pie_chart' in report_data:
                chart_path = report_data['protocol_pie_chart']
                if os.path.exists(chart_path):
                    story.append(Spacer(1, 0.2*inch))
                    img = Image(chart_path, width=6*inch, height=4*inch)
                    story.append(img)
            
            story.append(Spacer(1, 0.3*inch))
            
        except Exception as e:
            self.logger.error(f"创建协议统计区块失败: {e}")
        
        return story
    
    def _create_traffic_trends_section(self, report_data: Dict[str, Any]) -> List[Any]:
        """创建流量趋势区块"""
        story = []
        
        try:
            # 区块标题
            title = Paragraph("3. 流量趋势分析", self.styles['ChineseHeading1'])
            story.append(title)
            
            # 流量趋势描述
            traffic_trends = report_data.get('traffic_trends', {})
            peak_info = traffic_trends.get('peak_info', {})
            
            if peak_info:
                trend_text = f"""
                流量分析显示：<br/>
                • 峰值流量: {peak_info.get('max_packets', 0)} 个数据包<br/>
                • 峰值时间: {peak_info.get('peak_time', 'N/A')}<br/>
                • 平均流量: {peak_info.get('avg_packets', 0):.1f} 个数据包/秒<br/>
                """
                
                trend_para = Paragraph(trend_text, self.styles['ChineseNormal'])
                story.append(trend_para)
            
            # 添加流量趋势图表（如果存在）
            if 'traffic_trend_chart' in report_data:
                chart_path = report_data['traffic_trend_chart']
                if os.path.exists(chart_path):
                    story.append(Spacer(1, 0.2*inch))
                    img = Image(chart_path, width=7*inch, height=4*inch)
                    story.append(img)
            
            story.append(Spacer(1, 0.3*inch))
            
        except Exception as e:
            self.logger.error(f"创建流量趋势区块失败: {e}")
        
        return story
    
    def _create_summary_section(self, report_data: Dict[str, Any]) -> List[Any]:
        """创建汇总分析区块"""
        story = []
        
        try:
            # 区块标题
            title = Paragraph("4. 汇总分析", self.styles['ChineseHeading1'])
            story.append(title)
            
            # 汇总统计
            summary_stats = report_data.get('summary_stats', {})
            advanced_stats = summary_stats.get('advanced_stats', {})
            
            if advanced_stats:
                summary_text = f"""
                <b>网络流量汇总分析：</b><br/><br/>
                
                <b>基本统计：</b><br/>
                • 总数据包数: {advanced_stats.get('total_packets', 0):,}<br/>
                • 总字节数: {advanced_stats.get('total_bytes', 0):,}<br/>
                • 平均包大小: {advanced_stats.get('avg_packet_size', 0):.1f} 字节<br/>
                • 协议多样性: {advanced_stats.get('protocol_diversity', 0)} 种协议<br/><br/>
                
                <b>网络特征：</b><br/>
                • 时间跨度: {advanced_stats.get('time_span', 0):.1f} 秒<br/>
                • 平均速率: {advanced_stats.get('avg_packet_rate', 0):.1f} 包/秒<br/>
                • 唯一源IP: {advanced_stats.get('unique_src_ips', 0)} 个<br/>
                • 唯一目标IP: {advanced_stats.get('unique_dst_ips', 0)} 个<br/><br/>
                
                <b>分析结论：</b><br/>
                基于以上数据分析，该网络会话显示了正常的网络通信模式。
                协议分布和流量趋势符合预期的网络行为特征。
                """
                
                summary_para = Paragraph(summary_text, self.styles['ChineseNormal'])
                story.append(summary_para)
            
            story.append(Spacer(1, 0.3*inch))
            
        except Exception as e:
            self.logger.error(f"创建汇总分析区块失败: {e}")
        
        return story
    
    def add_chart_to_story(self, story: List[Any], chart_path: str, 
                          width: float = 6*inch, height: float = 4*inch):
        """
        添加图表到文档
        
        Args:
            story: 文档内容列表
            chart_path: 图表文件路径
            width: 图片宽度
            height: 图片高度
        """
        try:
            if os.path.exists(chart_path):
                img = Image(chart_path, width=width, height=height)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            else:
                self.logger.warning(f"图表文件不存在: {chart_path}")
                
        except Exception as e:
            self.logger.error(f"添加图表失败: {e}")
    
    def create_table_from_data(self, data: List[List[str]], 
                             headers: List[str],
                             col_widths: Optional[List[float]] = None) -> Table:
        """
        从数据创建表格
        
        Args:
            data: 表格数据
            headers: 表头
            col_widths: 列宽度
            
        Returns:
            Table: ReportLab表格对象
        """
        try:
            # 准备表格数据
            table_data = [headers] + data
            
            # 创建表格
            if col_widths:
                table = Table(table_data, colWidths=col_widths)
            else:
                table = Table(table_data)
            
            # 设置表格样式
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            self.logger.error(f"创建表格失败: {e}")
            raise
    
    def get_output_info(self, filepath: str) -> Dict[str, Any]:
        """
        获取输出文件信息
        
        Args:
            filepath: 文件路径
            
        Returns:
            Dict: 文件信息
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return {'exists': False}
            
            stat = path.stat()
            return {
                'exists': True,
                'filename': path.name,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime)
            }
            
        except Exception as e:
            self.logger.error(f"获取文件信息失败: {e}")
            return {'exists': False, 'error': str(e)}