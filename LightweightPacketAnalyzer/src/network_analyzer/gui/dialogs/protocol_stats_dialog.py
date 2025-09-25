"""
协议统计对话框

提供协议统计分析的图形界面，包括：
- 协议分布饼图
- 协议统计柱状图  
- 统计数据表格
- 过滤和导出功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import csv
import json

from network_analyzer.storage.data_manager import DataManager
from network_analyzer.statistics.protocol_statistics import ProtocolStatistics
from network_analyzer.statistics.statistics_visualizer import StatisticsVisualizer, ChartConfig


class ProtocolStatsDialog:
    """协议统计对话框"""
    
    def __init__(self, parent: tk.Tk, data_manager: DataManager, session_id: Optional[int] = None):
        """
        初始化协议统计对话框
        
        Args:
            parent: 父窗口
            data_manager: 数据管理器
            session_id: 会话ID，None表示使用当前会话
        """
        self.parent = parent
        self.data_manager = data_manager
        self.session_id = session_id
        self.logger = logging.getLogger(__name__)
        
        # 统计组件
        self.protocol_stats = ProtocolStatistics(data_manager)
        self.visualizer = StatisticsVisualizer()
        
        # 对话框窗口
        self.dialog = None
        self.result = None
        
        # UI组件
        self.session_var = None
        self.time_range_var = None
        self.chart_notebook = None
        self.stats_tree = None
        
        # 当前统计数据
        self.current_stats = None
        
    def show(self) -> Optional[Dict[str, Any]]:
        """
        显示对话框
        
        Returns:
            统计结果字典，如果用户取消则返回None
        """
        self._create_dialog()
        self._load_initial_data()
        
        # 模态显示
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # 等待对话框关闭
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def _create_dialog(self) -> None:
        """创建对话框界面"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("协议统计分析")
        self.dialog.geometry("1000x700")
        self.dialog.resizable(True, True)
        
        # 设置图标（如果有的话）
        try:
            self.dialog.iconbitmap(self.parent.iconbitmap())
        except:
            pass
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 创建控制面板
        self._create_control_panel(main_frame)
        
        # 创建内容区域
        self._create_content_area(main_frame)
        
        # 创建按钮区域
        self._create_button_area(main_frame)
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # 居中显示
        self._center_dialog()
    
    def _create_control_panel(self, parent: ttk.Frame) -> None:
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="过滤条件", padding="5")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(3, weight=1)
        
        # 会话选择
        ttk.Label(control_frame, text="会话:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.session_var = tk.StringVar()
        session_combo = ttk.Combobox(control_frame, textvariable=self.session_var, 
                                   state="readonly", width=20)
        session_combo.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # 时间范围选择
        ttk.Label(control_frame, text="时间范围:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.time_range_var = tk.StringVar(value="全部")
        time_combo = ttk.Combobox(control_frame, textvariable=self.time_range_var,
                                state="readonly", width=15)
        time_combo['values'] = ("全部", "最近1小时", "最近24小时", "最近7天", "自定义")
        time_combo.grid(row=0, column=3, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # 按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=4, sticky=tk.E)
        
        ttk.Button(button_frame, text="刷新", command=self._refresh_stats).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导出", command=self._export_stats).pack(side=tk.LEFT)
        
        # 绑定事件
        session_combo.bind('<<ComboboxSelected>>', self._on_session_changed)
        time_combo.bind('<<ComboboxSelected>>', self._on_time_range_changed)
    
    def _create_content_area(self, parent: ttk.Frame) -> None:
        """创建内容区域"""
        # 创建水平分割的PanedWindow
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左侧：图表区域
        chart_frame = ttk.LabelFrame(paned, text="统计图表", padding="5")
        paned.add(chart_frame, weight=2)
        
        # 创建图表选项卡
        self.chart_notebook = ttk.Notebook(chart_frame)
        self.chart_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 饼图选项卡
        pie_frame = ttk.Frame(self.chart_notebook)
        self.chart_notebook.add(pie_frame, text="协议分布")
        
        # 柱状图选项卡
        bar_frame = ttk.Frame(self.chart_notebook)
        self.chart_notebook.add(bar_frame, text="统计对比")
        
        # 右侧：数据表格
        table_frame = ttk.LabelFrame(paned, text="统计数据", padding="5")
        paned.add(table_frame, weight=1)
        
        self._create_stats_table(table_frame)
    
    def _create_stats_table(self, parent: ttk.Frame) -> None:
        """创建统计数据表格"""
        # 创建Treeview
        columns = ("protocol", "packets", "bytes", "packet_pct", "byte_pct", "avg_size")
        self.stats_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # 设置列标题
        self.stats_tree.heading("protocol", text="协议")
        self.stats_tree.heading("packets", text="数据包数")
        self.stats_tree.heading("bytes", text="字节数")
        self.stats_tree.heading("packet_pct", text="包占比(%)")
        self.stats_tree.heading("byte_pct", text="字节占比(%)")
        self.stats_tree.heading("avg_size", text="平均大小")
        
        # 设置列宽
        self.stats_tree.column("protocol", width=80, anchor=tk.CENTER)
        self.stats_tree.column("packets", width=80, anchor=tk.CENTER)
        self.stats_tree.column("bytes", width=100, anchor=tk.CENTER)
        self.stats_tree.column("packet_pct", width=80, anchor=tk.CENTER)
        self.stats_tree.column("byte_pct", width=80, anchor=tk.CENTER)
        self.stats_tree.column("avg_size", width=80, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_button_area(self, parent: ttk.Frame) -> None:
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, sticky=tk.E, pady=(10, 0))
        
        ttk.Button(button_frame, text="关闭", command=self._on_cancel).pack(side=tk.RIGHT)
    
    def _center_dialog(self) -> None:
        """居中显示对话框"""
        self.dialog.update_idletasks()
        
        # 获取对话框尺寸
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 获取父窗口位置和尺寸
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _load_initial_data(self) -> None:
        """加载初始数据"""
        try:
            # 加载会话列表
            self._load_sessions()
            
            # 设置默认会话
            if self.session_id:
                self.session_var.set(f"会话 {self.session_id}")
            else:
                # 使用当前会话或第一个会话
                sessions = self.session_var.get()
                if sessions:
                    self.session_var.set(sessions.split('\n')[0] if '\n' in sessions else sessions)
            
            # 加载统计数据
            self._refresh_stats()
            
        except Exception as e:
            self.logger.error(f"加载初始数据失败: {e}")
            messagebox.showerror("错误", f"加载数据失败: {e}")
    
    def _load_sessions(self) -> None:
        """加载会话列表"""
        try:
            sessions = self.data_manager.get_sessions()
            session_options = []
            
            for session in sessions:
                session_name = session.get('name', f'会话 {session["id"]}')
                session_options.append(f"{session_name} (ID: {session['id']})")
            
            if session_options:
                # 更新会话下拉框
                session_combo = None
                for child in self.dialog.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.LabelFrame) and grandchild.cget('text') == '过滤条件':
                                for widget in grandchild.winfo_children():
                                    if isinstance(widget, ttk.Combobox) and widget.cget('textvariable') == str(self.session_var):
                                        session_combo = widget
                                        break
                
                if session_combo:
                    session_combo['values'] = session_options
                    if not self.session_var.get() and session_options:
                        self.session_var.set(session_options[0])
            else:
                messagebox.showwarning("警告", "没有找到任何会话数据")
                
        except Exception as e:
            self.logger.error(f"加载会话列表失败: {e}")
            messagebox.showerror("错误", f"加载会话列表失败: {e}")
    
    def _get_current_session_id(self) -> Optional[int]:
        """获取当前选中的会话ID"""
        session_text = self.session_var.get()
        if not session_text:
            return None
        
        try:
            # 从 "会话名 (ID: 123)" 格式中提取ID
            if "(ID: " in session_text:
                id_part = session_text.split("(ID: ")[1].rstrip(")")
                return int(id_part)
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _refresh_stats(self) -> None:
        """刷新统计数据"""
        try:
            session_id = self._get_current_session_id()
            if not session_id:
                messagebox.showwarning("警告", "请选择一个会话")
                return
            
            # 获取时间范围过滤条件
            time_filter = self._get_time_filter()
            
            # 获取协议分布数据
            from network_analyzer.statistics.protocol_statistics import StatisticsFilter
            filter_params = StatisticsFilter(
                session_id=session_id,
                start_time=time_filter.get('start') if time_filter else None,
                end_time=time_filter.get('end') if time_filter else None
            )
            distribution = self.protocol_stats.get_protocol_distribution(filter_params)
            self.current_stats = distribution
            
            if not self.current_stats or not self.current_stats.protocol_counts:
                messagebox.showinfo("信息", "当前条件下没有找到数据包")
                self._clear_display()
                return
            
            # 更新显示
            self._update_charts()
            self._update_table()
            
        except Exception as e:
            self.logger.error(f"刷新统计数据失败: {e}")
            messagebox.showerror("错误", f"刷新统计数据失败: {e}")
    
    def _get_time_filter(self) -> Optional[tuple]:
        """获取时间过滤条件"""
        time_range = self.time_range_var.get()
        
        if time_range == "全部":
            return None
        
        # 这里可以根据需要实现具体的时间范围逻辑
        # 暂时返回None表示不过滤
        return None
    
    def _update_charts(self) -> None:
        """更新图表显示"""
        if not self.current_stats:
            return
        
        try:
            # 获取图表框架
            pie_frame = self.chart_notebook.nametowidget(self.chart_notebook.tabs()[0])
            bar_frame = self.chart_notebook.nametowidget(self.chart_notebook.tabs()[1])
            
            # 清除现有图表
            for widget in pie_frame.winfo_children():
                widget.destroy()
            for widget in bar_frame.winfo_children():
                widget.destroy()
            
            # 创建饼图
            pie_config = ChartConfig(
                title="协议分布",
                figsize=(6, 4)
            )
            pie_canvas = self.visualizer.create_pie_chart(self.current_stats, pie_config, pie_frame)
            if pie_canvas:
                pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # 创建柱状图
            bar_config = ChartConfig(
                title="协议统计对比",
                figsize=(6, 4),
                xlabel="协议类型",
                ylabel="数据包数量"
            )
            bar_canvas = self.visualizer.create_bar_chart(self.current_stats, bar_config, bar_frame)
            if bar_canvas:
                bar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
        except Exception as e:
            self.logger.error(f"更新图表失败: {e}")
            messagebox.showerror("错误", f"更新图表失败: {e}")
    
    def _update_table(self) -> None:
        """更新数据表格"""
        if not self.current_stats:
            return
        
        try:
            # 清除现有数据
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            # 添加统计数据
            total_packets = self.current_stats.total_packets
            total_bytes = self.current_stats.total_bytes
            
            for protocol, count in self.current_stats.protocol_counts.items():
                bytes_count = self.current_stats.protocol_bytes.get(protocol, 0)
                packet_pct = (count / total_packets * 100) if total_packets > 0 else 0
                byte_pct = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                avg_size = (bytes_count / count) if count > 0 else 0
                
                self.stats_tree.insert("", tk.END, values=(
                    protocol,
                    f"{count:,}",
                    f"{bytes_count:,}",
                    f"{packet_pct:.1f}",
                    f"{byte_pct:.1f}",
                    f"{avg_size:.0f}"
                ))
            
            # 添加总计行
            self.stats_tree.insert("", tk.END, values=(
                "总计",
                f"{total_packets:,}",
                f"{total_bytes:,}",
                "100.0",
                "100.0",
                f"{total_bytes/total_packets:.0f}" if total_packets > 0 else "0"
            ))
            
        except Exception as e:
            self.logger.error(f"更新表格失败: {e}")
            messagebox.showerror("错误", f"更新表格失败: {e}")
    
    def _clear_display(self) -> None:
        """清除显示内容"""
        # 清除图表
        if self.chart_notebook:
            for tab_id in self.chart_notebook.tabs():
                frame = self.chart_notebook.nametowidget(tab_id)
                for widget in frame.winfo_children():
                    widget.destroy()
        
        # 清除表格
        if self.stats_tree:
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
    
    def _export_stats(self) -> None:
        """导出统计数据"""
        if not self.current_stats:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
        
        try:
            # 选择导出文件
            filename = filedialog.asksaveasfilename(
                title="导出统计数据",
                defaultextension=".csv",
                filetypes=[
                    ("CSV文件", "*.csv"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not filename:
                return
            
            if filename.lower().endswith('.csv'):
                self._export_to_csv(filename)
            elif filename.lower().endswith('.json'):
                self._export_to_json(filename)
            else:
                messagebox.showerror("错误", "不支持的文件格式")
                return
            
            messagebox.showinfo("成功", f"数据已导出到: {filename}")
            
        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            messagebox.showerror("错误", f"导出数据失败: {e}")
    
    def _export_to_csv(self, filename: str) -> None:
        """导出为CSV格式"""
        # 使用UTF-8 BOM编码，确保Excel等软件能正确识别中文
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入标题
            writer.writerow(['协议', '数据包数', '字节数', '包占比(%)', '字节占比(%)', '平均大小'])
            
            # 写入数据
            total_packets = self.current_stats.total_packets
            total_bytes = self.current_stats.total_bytes
            
            for protocol, count in self.current_stats.protocol_counts.items():
                bytes_count = self.current_stats.protocol_bytes.get(protocol, 0)
                packet_pct = (count / total_packets * 100) if total_packets > 0 else 0
                byte_pct = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                avg_size = (bytes_count / count) if count > 0 else 0
                
                writer.writerow([
                    protocol, count, bytes_count, 
                    f"{packet_pct:.1f}", f"{byte_pct:.1f}", f"{avg_size:.0f}"
                ])
    
    def _export_to_json(self, filename: str) -> None:
        """导出为JSON格式"""
        data = {
            'export_time': datetime.now().isoformat(),
            'session_id': self._get_current_session_id(),
            'time_range': self.time_range_var.get(),
            'total_packets': self.current_stats.total_packets,
            'total_bytes': self.current_stats.total_bytes,
            'time_range_info': {
                'start': self.current_stats.time_range[0],
                'end': self.current_stats.time_range[1]
            },
            'protocols': {}
        }
        
        for protocol, count in self.current_stats.protocol_counts.items():
            bytes_count = self.current_stats.protocol_bytes.get(protocol, 0)
            packet_pct = (count / self.current_stats.total_packets * 100) if self.current_stats.total_packets > 0 else 0
            byte_pct = (bytes_count / self.current_stats.total_bytes * 100) if self.current_stats.total_bytes > 0 else 0
            
            data['protocols'][protocol] = {
                'packet_count': count,
                'byte_count': bytes_count,
                'packet_percentage': round(packet_pct, 2),
                'byte_percentage': round(byte_pct, 2),
                'average_size': round(bytes_count / count, 2) if count > 0 else 0
            }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    def _on_session_changed(self, event=None) -> None:
        """会话选择改变事件"""
        self._refresh_stats()
    
    def _on_time_range_changed(self, event=None) -> None:
        """时间范围改变事件"""
        self._refresh_stats()
    
    def _on_cancel(self) -> None:
        """取消按钮事件"""
        self.result = None
        self.dialog.destroy()