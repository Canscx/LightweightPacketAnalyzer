"""
流量趋势对话框

提供流量趋势的可视化显示和交互功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from ..storage.data_manager import DataManager
from ..processing.traffic_data_processor import TrafficDataProcessor
from .chart_manager import ChartManager


class TrafficTrendsDialog:
    """流量趋势对话框类"""
    
    def __init__(self, parent: tk.Tk, data_manager: DataManager):
        """
        初始化流量趋势对话框
        
        Args:
            parent: 父窗口
            data_manager: 数据管理器实例
        """
        self.parent = parent
        self.data_manager = data_manager
        self.data_processor = TrafficDataProcessor()
        self.logger = logging.getLogger(__name__)
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("网络流量趋势分析")
        self.dialog.geometry("1200x800")
        self.dialog.resizable(True, True)
        
        # 居中显示
        self._center_dialog()
        
        # 实时更新控制
        self.update_thread = None
        self.is_updating = False
        self.update_interval = 1  # 秒
        
        # 协议过滤状态
        self.protocol_vars = {}
        self.available_protocols = ['TCP', 'UDP', 'ICMP', 'DNS']
        
        # 时间范围设置
        self.time_range_minutes = 5  # 默认5分钟
        
        # 创建UI组件
        self._create_ui()
        
        # 初始化图表管理器
        self.chart_manager = ChartManager(self.chart_frame)
        
        # 绑定窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 启动初始数据加载
        self._load_initial_data()
        
        self.logger.info("流量趋势对话框初始化完成")
    
    def _center_dialog(self) -> None:
        """居中显示对话框"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self) -> None:
        """创建用户界面"""
        try:
            # 创建主框架
            main_frame = ttk.Frame(self.dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 创建控制面板
            self._create_control_panel(main_frame)
            
            # 创建图表区域
            self._create_chart_area(main_frame)
            
            # 创建状态栏
            self._create_status_bar(main_frame)
            
        except Exception as e:
            self.logger.error(f"创建UI失败: {e}")
    
    def _create_control_panel(self, parent: ttk.Frame) -> None:
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行：时间范围和更新控制
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 时间范围选择
        ttk.Label(row1_frame, text="时间范围:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.time_range_var = tk.StringVar(value="5分钟")
        time_range_combo = ttk.Combobox(
            row1_frame, 
            textvariable=self.time_range_var,
            values=["1分钟", "5分钟", "10分钟", "30分钟", "1小时"],
            state="readonly",
            width=10
        )
        time_range_combo.pack(side=tk.LEFT, padx=(0, 20))
        time_range_combo.bind('<<ComboboxSelected>>', self._on_time_range_change)
        
        # 实时更新控制
        self.auto_update_var = tk.BooleanVar(value=True)
        auto_update_check = ttk.Checkbutton(
            row1_frame,
            text="实时更新",
            variable=self.auto_update_var,
            command=self._toggle_auto_update
        )
        auto_update_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # 手动刷新按钮
        refresh_btn = ttk.Button(
            row1_frame,
            text="手动刷新",
            command=self._manual_refresh
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        # 导出按钮
        export_btn = ttk.Button(
            row1_frame,
            text="导出PNG",
            command=self._export_chart
        )
        export_btn.pack(side=tk.RIGHT)
        
        # 第二行：协议过滤
        row2_frame = ttk.LabelFrame(control_frame, text="协议过滤", padding=5)
        row2_frame.pack(fill=tk.X)
        
        # 创建协议复选框
        for i, protocol in enumerate(self.available_protocols):
            var = tk.BooleanVar(value=True)
            self.protocol_vars[protocol] = var
            
            checkbox = ttk.Checkbutton(
                row2_frame,
                text=protocol,
                variable=var,
                command=lambda p=protocol: self._toggle_protocol(p)
            )
            checkbox.grid(row=0, column=i, padx=10, pady=5, sticky=tk.W)
        
        # 全选/全不选按钮
        button_frame = ttk.Frame(row2_frame)
        button_frame.grid(row=0, column=len(self.available_protocols), padx=20)
        
        ttk.Button(
            button_frame,
            text="全选",
            command=self._select_all_protocols,
            width=8
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="全不选",
            command=self._deselect_all_protocols,
            width=8
        ).pack(side=tk.LEFT, padx=2)
    
    def _create_chart_area(self, parent: ttk.Frame) -> None:
        """创建图表区域"""
        # 图表框架
        self.chart_frame = ttk.LabelFrame(parent, text="流量趋势图表", padding=5)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self, parent: ttk.Frame) -> None:
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # 数据统计显示
        self.stats_var = tk.StringVar(value="")
        stats_label = ttk.Label(status_frame, textvariable=self.stats_var)
        stats_label.pack(side=tk.RIGHT)
    
    def _load_initial_data(self) -> None:
        """加载初始数据"""
        try:
            self.status_var.set("加载初始数据...")
            self._refresh_data()
            
            # 启动自动更新
            if self.auto_update_var.get():
                self._start_auto_update()
                
        except Exception as e:
            self.logger.error(f"加载初始数据失败: {e}")
            self.status_var.set(f"加载失败: {e}")
    
    def _refresh_data(self) -> None:
        """刷新数据"""
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=self.time_range_minutes)
            
            # 获取选中的协议
            selected_protocols = [
                protocol for protocol, var in self.protocol_vars.items()
                if var.get()
            ]
            
            if not selected_protocols:
                self.status_var.set("请至少选择一个协议")
                return
            
            # 查询数据
            data = self.data_manager.get_traffic_trends_data(
                start_time=start_time,
                end_time=end_time,
                protocols=selected_protocols
            )
            
            if data and data['timestamps']:
                # 创建或更新图表
                if not self.chart_manager.protocol_lines:
                    # 首次创建图表
                    self.chart_manager.create_trends_chart(data)
                else:
                    # 更新现有图表
                    self.chart_manager.update_chart_data(data)
                
                # 更新统计信息
                self._update_statistics(data)
                
                self.status_var.set(f"最后更新: {datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_var.set("暂无数据")
                # 创建空图表
                self.chart_manager._create_empty_chart()
                
        except Exception as e:
            self.logger.error(f"刷新数据失败: {e}")
            self.status_var.set(f"刷新失败: {e}")
    
    def _update_statistics(self, data: Dict[str, Any]) -> None:
        """更新统计信息"""
        try:
            total_packets = 0
            protocol_counts = {}
            
            for protocol, values in data['data'].items():
                count = sum(values.get('counts', []))
                total_packets += count
                protocol_counts[protocol] = count
            
            # 格式化统计信息
            stats_text = f"总数据包: {total_packets}"
            if protocol_counts:
                protocol_stats = ", ".join([
                    f"{protocol}: {count}" 
                    for protocol, count in protocol_counts.items()
                    if count > 0
                ])
                if protocol_stats:
                    stats_text += f" | {protocol_stats}"
            
            self.stats_var.set(stats_text)
            
        except Exception as e:
            self.logger.error(f"更新统计信息失败: {e}")
    
    def _start_auto_update(self) -> None:
        """启动自动更新"""
        if not self.is_updating:
            self.is_updating = True
            self.update_thread = threading.Thread(target=self._auto_update_loop, daemon=True)
            self.update_thread.start()
            self.logger.info("自动更新已启动")
    
    def _stop_auto_update(self) -> None:
        """停止自动更新"""
        self.is_updating = False
        if self.update_thread:
            self.update_thread = None
        self.logger.info("自动更新已停止")
    
    def _auto_update_loop(self) -> None:
        """自动更新循环"""
        while self.is_updating:
            try:
                # 在主线程中更新UI
                self.dialog.after(0, self._refresh_data)
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"自动更新循环异常: {e}")
                break
    
    def _on_time_range_change(self, event=None) -> None:
        """时间范围改变事件"""
        try:
            range_text = self.time_range_var.get()
            
            # 解析时间范围
            if "分钟" in range_text:
                self.time_range_minutes = int(range_text.replace("分钟", ""))
            elif "小时" in range_text:
                hours = int(range_text.replace("小时", ""))
                self.time_range_minutes = hours * 60
            
            # 刷新数据
            self._refresh_data()
            
            self.logger.debug(f"时间范围已更改为: {self.time_range_minutes}分钟")
            
        except Exception as e:
            self.logger.error(f"时间范围改变处理失败: {e}")
    
    def _toggle_auto_update(self) -> None:
        """切换自动更新"""
        if self.auto_update_var.get():
            self._start_auto_update()
        else:
            self._stop_auto_update()
    
    def _manual_refresh(self) -> None:
        """手动刷新"""
        self._refresh_data()
    
    def _export_chart(self) -> None:
        """导出图表"""
        try:
            success = self.chart_manager.export_to_png()
            if success:
                self.logger.info("图表导出成功")
        except Exception as e:
            self.logger.error(f"导出图表失败: {e}")
            messagebox.showerror("导出失败", f"导出图表时发生错误:\n{e}")
    
    def _toggle_protocol(self, protocol: str) -> None:
        """切换协议显示"""
        try:
            visible = self.protocol_vars[protocol].get()
            self.chart_manager.toggle_protocol_line(protocol, visible)
            
            # 如果没有协议被选中，至少保持一个
            selected_count = sum(1 for var in self.protocol_vars.values() if var.get())
            if selected_count == 0:
                self.protocol_vars[protocol].set(True)
                self.chart_manager.toggle_protocol_line(protocol, True)
                messagebox.showwarning("警告", "至少需要选择一个协议")
                return
            
            # 刷新数据
            self._refresh_data()
            
            self.logger.debug(f"协议 {protocol} 显示状态: {visible}")
            
        except Exception as e:
            self.logger.error(f"切换协议显示失败: {e}")
    
    def _select_all_protocols(self) -> None:
        """全选协议"""
        for var in self.protocol_vars.values():
            var.set(True)
        
        # 更新图表显示
        for protocol in self.available_protocols:
            self.chart_manager.toggle_protocol_line(protocol, True)
        
        self._refresh_data()
    
    def _deselect_all_protocols(self) -> None:
        """全不选协议（保留一个）"""
        # 保留第一个协议
        first_protocol = self.available_protocols[0]
        
        for protocol, var in self.protocol_vars.items():
            if protocol == first_protocol:
                var.set(True)
                self.chart_manager.toggle_protocol_line(protocol, True)
            else:
                var.set(False)
                self.chart_manager.toggle_protocol_line(protocol, False)
        
        self._refresh_data()
        messagebox.showinfo("提示", f"已保留 {first_protocol} 协议显示")
    
    def _on_close(self) -> None:
        """窗口关闭事件"""
        try:
            # 停止自动更新
            self._stop_auto_update()
            
            # 销毁图表管理器
            if hasattr(self, 'chart_manager'):
                self.chart_manager.destroy()
            
            # 关闭对话框
            self.dialog.destroy()
            
            self.logger.info("流量趋势对话框已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭对话框失败: {e}")
    
    def show(self) -> None:
        """显示对话框"""
        self.dialog.focus_set()
        self.dialog.grab_set()
    
    def get_dialog(self) -> tk.Toplevel:
        """获取对话框窗口对象"""
        return self.dialog