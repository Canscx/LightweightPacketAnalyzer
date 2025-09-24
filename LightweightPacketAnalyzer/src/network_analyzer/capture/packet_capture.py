"""
网络数据包捕获模块

使用Scapy库实现网络数据包的实时捕获功能。
"""

import threading
import time
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime
import logging

try:
    from scapy.all import sniff, get_if_list, conf
    from scapy.packet import Packet
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    Packet = Any

from ..config.settings import Settings


class PacketCapture:
    """网络数据包捕获类"""
    
    def __init__(self, settings: Settings):
        """
        初始化数据包捕获器
        
        Args:
            settings: 配置对象
        """
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # 检查Scapy是否可用
        if not SCAPY_AVAILABLE:
            raise ImportError("Scapy库未安装，请运行: pip install scapy")
        
        # 捕获状态
        self._is_capturing = False
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # 统计信息
        self._packet_count = 0
        self._start_time: Optional[datetime] = None
        
        # 回调函数
        self._packet_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # 捕获参数
        self._interface: Optional[str] = None
        self._filter_expression: str = ""
        
    def get_available_interfaces(self) -> List[str]:
        """
        获取可用的网络接口列表
        
        Returns:
            可用网络接口列表
        """
        try:
            interfaces = get_if_list()
            self.logger.info(f"发现 {len(interfaces)} 个网络接口")
            return interfaces
        except Exception as e:
            self.logger.error(f"获取网络接口失败: {e}")
            return []
    
    def set_packet_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        设置数据包处理回调函数
        
        Args:
            callback: 数据包处理回调函数，接收数据包字典作为参数
        """
        self._packet_callback = callback
    
    def start_capture(self, 
                     interface: Optional[str] = None,
                     filter_expression: str = "",
                     timeout: Optional[float] = None) -> bool:
        """
        开始数据包捕获
        
        Args:
            interface: 网络接口名称，None表示使用默认接口
            filter_expression: BPF过滤表达式
            timeout: 捕获超时时间（秒），None表示无限制
            
        Returns:
            是否成功开始捕获
        """
        if self._is_capturing:
            self.logger.warning("数据包捕获已在进行中")
            return False
        
        try:
            self._interface = interface
            self._filter_expression = filter_expression
            self._stop_event.clear()
            
            # 创建并启动捕获线程
            self._capture_thread = threading.Thread(
                target=self._capture_worker,
                args=(timeout,),
                daemon=True
            )
            
            self._is_capturing = True
            self._packet_count = 0
            self._start_time = datetime.now()
            
            self._capture_thread.start()
            
            self.logger.info(f"开始数据包捕获 - 接口: {interface or '默认'}, 过滤器: {filter_expression or '无'}")
            return True
            
        except Exception as e:
            self.logger.error(f"启动数据包捕获失败: {e}")
            self._is_capturing = False
            return False
    
    def stop_capture(self) -> bool:
        """
        停止数据包捕获
        
        Returns:
            是否成功停止捕获
        """
        if not self._is_capturing:
            self.logger.warning("数据包捕获未在进行中")
            return False
        
        try:
            self._stop_event.set()
            self._is_capturing = False
            
            # 等待捕获线程结束
            if self._capture_thread and self._capture_thread.is_alive():
                self._capture_thread.join(timeout=5.0)
            
            duration = (datetime.now() - self._start_time).total_seconds() if self._start_time else 0
            self.logger.info(f"数据包捕获已停止 - 总计: {self._packet_count} 个数据包, 耗时: {duration:.2f} 秒")
            
            return True
            
        except Exception as e:
            self.logger.error(f"停止数据包捕获失败: {e}")
            return False
    
    def _capture_worker(self, timeout: Optional[float]) -> None:
        """
        数据包捕获工作线程
        
        Args:
            timeout: 捕获超时时间
        """
        try:
            # 设置捕获参数
            capture_kwargs = {
                'prn': self._process_packet,
                'store': False,  # 不存储数据包到内存
                'stop_filter': lambda x: self._stop_event.is_set()
            }
            
            if self._interface:
                capture_kwargs['iface'] = self._interface
            
            if self._filter_expression:
                capture_kwargs['filter'] = self._filter_expression
            
            if timeout:
                capture_kwargs['timeout'] = timeout
            
            # 开始捕获
            sniff(**capture_kwargs)
            
        except Exception as e:
            self.logger.error(f"数据包捕获线程异常: {e}")
        finally:
            self._is_capturing = False
    
    def _process_packet(self, packet: Packet) -> None:
        """
        处理捕获到的数据包
        
        Args:
            packet: Scapy数据包对象
        """
        try:
            # 更新统计信息
            self._packet_count += 1
            
            # 提取数据包信息
            packet_info = self._extract_packet_info(packet)
            
            # 调用回调函数
            if self._packet_callback:
                self._packet_callback(packet_info)
                
        except Exception as e:
            self.logger.error(f"处理数据包失败: {e}")
    
    def _extract_packet_info(self, packet: Packet) -> Dict[str, Any]:
        """
        从Scapy数据包对象中提取信息
        
        Args:
            packet: Scapy数据包对象
            
        Returns:
            数据包信息字典
        """
        info = {
            'timestamp': time.time(),
            'length': len(packet),
            'protocol': 'Unknown',
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dst_port': None,
            'summary': packet.summary(),
            'raw_data': bytes(packet)  # 添加原始数据包字节数据
        }
        
        try:
            # 提取IP层信息
            if packet.haslayer('IP'):
                ip_layer = packet['IP']
                info['src_ip'] = ip_layer.src
                info['dst_ip'] = ip_layer.dst
                info['protocol'] = ip_layer.proto
            
            # 提取传输层信息
            if packet.haslayer('TCP'):
                tcp_layer = packet['TCP']
                info['src_port'] = tcp_layer.sport
                info['dst_port'] = tcp_layer.dport
                info['protocol'] = 'TCP'
            elif packet.haslayer('UDP'):
                udp_layer = packet['UDP']
                info['src_port'] = udp_layer.sport
                info['dst_port'] = udp_layer.dport
                info['protocol'] = 'UDP'
            elif packet.haslayer('ICMP'):
                info['protocol'] = 'ICMP'
            
            # 提取应用层协议信息
            if packet.haslayer('HTTP'):
                info['protocol'] = 'HTTP'
            elif packet.haslayer('DNS'):
                info['protocol'] = 'DNS'
            elif packet.haslayer('DHCP'):
                info['protocol'] = 'DHCP'
                
        except Exception as e:
            self.logger.debug(f"提取数据包信息时出错: {e}")
        
        return info
    
    @property
    def is_capturing(self) -> bool:
        """是否正在捕获数据包"""
        return self._is_capturing
    
    @property
    def packet_count(self) -> int:
        """已捕获的数据包数量"""
        return self._packet_count
    
    @property
    def capture_duration(self) -> float:
        """捕获持续时间（秒）"""
        if not self._start_time:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()
    
    def get_capture_stats(self) -> Dict[str, Any]:
        """
        获取捕获统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'is_capturing': self.is_capturing,
            'packet_count': self.packet_count,
            'duration': self.capture_duration,
            'interface': self._interface,
            'filter': self._filter_expression,
            'start_time': self._start_time.isoformat() if self._start_time else None
        }