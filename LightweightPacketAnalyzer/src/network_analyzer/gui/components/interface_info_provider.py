"""
网络接口信息提供器

提供详细的网络接口信息获取功能。
"""

import logging
import platform
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from scapy.all import get_if_list, get_if_addr, get_if_hwaddr
    import psutil
    SCAPY_AVAILABLE = True
    PSUTIL_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    try:
        import psutil
        PSUTIL_AVAILABLE = True
    except ImportError:
        PSUTIL_AVAILABLE = False


@dataclass
class InterfaceInfo:
    """网络接口信息数据类"""
    name: str
    display_name: str
    description: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    is_up: bool = False
    is_loopback: bool = False
    mtu: Optional[int] = None
    speed: Optional[int] = None  # Mbps
    interface_type: str = "Unknown"
    statistics: Optional[Dict[str, int]] = None


class InterfaceInfoProvider:
    """网络接口信息提供器"""
    
    def __init__(self):
        """初始化接口信息提供器"""
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        
        # 检查依赖库可用性
        if not SCAPY_AVAILABLE:
            self.logger.warning("Scapy不可用，接口信息功能受限")
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil不可用，接口统计信息不可用")
    
    def get_all_interfaces(self) -> List[InterfaceInfo]:
        """
        获取所有网络接口信息
        
        Returns:
            接口信息列表
        """
        interfaces = []
        
        try:
            if SCAPY_AVAILABLE:
                # 使用Scapy获取基本接口列表
                interface_names = get_if_list()
            else:
                # 回退到psutil
                interface_names = list(psutil.net_if_addrs().keys()) if PSUTIL_AVAILABLE else []
            
            for name in interface_names:
                try:
                    info = self._get_interface_info(name)
                    if info:
                        interfaces.append(info)
                except Exception as e:
                    self.logger.debug(f"获取接口 {name} 信息失败: {e}")
                    # 创建基本信息
                    interfaces.append(InterfaceInfo(
                        name=name,
                        display_name=name,
                        description=f"网络接口 {name}",
                        interface_type="Unknown"
                    ))
            
            # 按名称排序，但将回环接口放在最后
            interfaces.sort(key=lambda x: (x.is_loopback, x.name))
            
            self.logger.info(f"发现 {len(interfaces)} 个网络接口")
            return interfaces
            
        except Exception as e:
            self.logger.error(f"获取网络接口列表失败: {e}")
            return []
    
    def _get_interface_info(self, interface_name: str) -> Optional[InterfaceInfo]:
        """
        获取单个接口的详细信息
        
        Args:
            interface_name: 接口名称
            
        Returns:
            接口信息对象
        """
        try:
            info = InterfaceInfo(
                name=interface_name,
                display_name=interface_name,
                description=f"网络接口 {interface_name}"
            )
            
            # 使用Scapy获取基本信息
            if SCAPY_AVAILABLE:
                try:
                    info.ip_address = get_if_addr(interface_name)
                    info.mac_address = get_if_hwaddr(interface_name)
                except:
                    pass
            
            # 使用psutil获取详细信息
            if PSUTIL_AVAILABLE:
                self._enhance_with_psutil(info)
            
            # 系统特定的增强
            if self.system == "windows":
                self._enhance_windows_info(info)
            elif self.system == "linux":
                self._enhance_linux_info(info)
            elif self.system == "darwin":
                self._enhance_macos_info(info)
            
            return info
            
        except Exception as e:
            self.logger.debug(f"获取接口 {interface_name} 详细信息失败: {e}")
            return None
    
    def _enhance_with_psutil(self, info: InterfaceInfo):
        """使用psutil增强接口信息"""
        try:
            # 获取地址信息
            addrs = psutil.net_if_addrs().get(info.name, [])
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    if not info.ip_address:
                        info.ip_address = addr.address
                elif addr.family == 17:  # AF_PACKET (MAC)
                    if not info.mac_address:
                        info.mac_address = addr.address
            
            # 获取状态信息
            stats = psutil.net_if_stats().get(info.name)
            if stats:
                info.is_up = stats.isup
                info.mtu = stats.mtu
                info.speed = stats.speed if stats.speed > 0 else None
            
            # 获取统计信息
            counters = psutil.net_io_counters(pernic=True).get(info.name)
            if counters:
                info.statistics = {
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errin': counters.errin,
                    'errout': counters.errout,
                    'dropin': counters.dropin,
                    'dropout': counters.dropout
                }
            
            # 判断接口类型
            info.is_loopback = info.name.lower().startswith(('lo', 'loopback'))
            
            if info.is_loopback:
                info.interface_type = "Loopback"
                info.description = "回环接口"
            elif info.name.lower().startswith(('eth', 'en')):
                info.interface_type = "Ethernet"
                info.description = "以太网接口"
            elif info.name.lower().startswith(('wlan', 'wi-fi', 'wireless')):
                info.interface_type = "Wireless"
                info.description = "无线网络接口"
            elif info.name.lower().startswith('ppp'):
                info.interface_type = "PPP"
                info.description = "点对点协议接口"
            elif info.name.lower().startswith('tun'):
                info.interface_type = "Tunnel"
                info.description = "隧道接口"
            
        except Exception as e:
            self.logger.debug(f"psutil增强接口信息失败: {e}")
    
    def _enhance_windows_info(self, info: InterfaceInfo):
        """增强Windows系统的接口信息"""
        try:
            # 使用wmic获取更详细的信息
            cmd = f'wmic path win32_networkadapter where "NetConnectionID=\\"{info.name}\\"" get Name,NetConnectionStatus,Speed /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # 跳过标题行
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            info.display_name = parts[1] if parts[1] else info.name
                            # 解析连接状态和速度等信息
            
        except Exception as e:
            self.logger.debug(f"Windows接口信息增强失败: {e}")
    
    def _enhance_linux_info(self, info: InterfaceInfo):
        """增强Linux系统的接口信息"""
        try:
            # 读取/sys/class/net/下的信息
            import os
            net_path = f"/sys/class/net/{info.name}"
            
            if os.path.exists(net_path):
                # 读取接口类型
                type_file = os.path.join(net_path, "type")
                if os.path.exists(type_file):
                    with open(type_file, 'r') as f:
                        type_num = int(f.read().strip())
                        if type_num == 1:
                            info.interface_type = "Ethernet"
                        elif type_num == 772:
                            info.interface_type = "Loopback"
                
                # 读取操作状态
                operstate_file = os.path.join(net_path, "operstate")
                if os.path.exists(operstate_file):
                    with open(operstate_file, 'r') as f:
                        state = f.read().strip()
                        info.is_up = state == "up"
                
                # 读取MTU
                mtu_file = os.path.join(net_path, "mtu")
                if os.path.exists(mtu_file):
                    with open(mtu_file, 'r') as f:
                        info.mtu = int(f.read().strip())
            
        except Exception as e:
            self.logger.debug(f"Linux接口信息增强失败: {e}")
    
    def _enhance_macos_info(self, info: InterfaceInfo):
        """增强macOS系统的接口信息"""
        try:
            # 使用ifconfig获取详细信息
            result = subprocess.run(['ifconfig', info.name], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                output = result.stdout
                
                # 解析状态
                if 'UP' in output:
                    info.is_up = True
                
                # 解析MTU
                import re
                mtu_match = re.search(r'mtu (\d+)', output)
                if mtu_match:
                    info.mtu = int(mtu_match.group(1))
                
                # 解析接口类型
                if 'loopback' in output.lower():
                    info.interface_type = "Loopback"
                    info.is_loopback = True
                elif 'ethernet' in output.lower():
                    info.interface_type = "Ethernet"
            
        except Exception as e:
            self.logger.debug(f"macOS接口信息增强失败: {e}")
    
    def get_interface_by_name(self, name: str) -> Optional[InterfaceInfo]:
        """
        根据名称获取接口信息
        
        Args:
            name: 接口名称
            
        Returns:
            接口信息对象
        """
        return self._get_interface_info(name)
    
    def get_active_interfaces(self) -> List[InterfaceInfo]:
        """
        获取活动的网络接口
        
        Returns:
            活动接口列表
        """
        all_interfaces = self.get_all_interfaces()
        return [iface for iface in all_interfaces if iface.is_up and not iface.is_loopback]
    
    def get_capture_suitable_interfaces(self) -> List[InterfaceInfo]:
        """
        获取适合数据包捕获的接口
        
        Returns:
            适合捕获的接口列表
        """
        all_interfaces = self.get_all_interfaces()
        suitable = []
        
        for iface in all_interfaces:
            # 排除回环接口（除非是唯一选择）
            if iface.is_loopback:
                continue
            
            # 优先选择有IP地址的活动接口
            if iface.is_up and iface.ip_address:
                suitable.append(iface)
            # 也包括未激活但有MAC地址的接口（可能可以激活）
            elif iface.mac_address:
                suitable.append(iface)
        
        # 如果没有合适的接口，包括回环接口
        if not suitable:
            suitable = [iface for iface in all_interfaces if iface.is_loopback]
        
        return suitable
    
    def format_interface_info(self, info: InterfaceInfo) -> str:
        """
        格式化接口信息为可读字符串
        
        Args:
            info: 接口信息对象
            
        Returns:
            格式化的信息字符串
        """
        lines = [f"接口: {info.display_name} ({info.name})"]
        lines.append(f"类型: {info.interface_type}")
        lines.append(f"描述: {info.description}")
        
        if info.ip_address:
            lines.append(f"IP地址: {info.ip_address}")
        
        if info.mac_address:
            lines.append(f"MAC地址: {info.mac_address}")
        
        lines.append(f"状态: {'启用' if info.is_up else '禁用'}")
        
        if info.mtu:
            lines.append(f"MTU: {info.mtu}")
        
        if info.speed:
            lines.append(f"速度: {info.speed} Mbps")
        
        if info.statistics:
            lines.append("统计信息:")
            stats = info.statistics
            lines.append(f"  发送: {stats.get('packets_sent', 0)} 包, {stats.get('bytes_sent', 0)} 字节")
            lines.append(f"  接收: {stats.get('packets_recv', 0)} 包, {stats.get('bytes_recv', 0)} 字节")
            if stats.get('errin', 0) > 0 or stats.get('errout', 0) > 0:
                lines.append(f"  错误: 入 {stats.get('errin', 0)}, 出 {stats.get('errout', 0)}")
        
        return "\n".join(lines)
    
    def refresh_interface_info(self, interface_name: str) -> Optional[InterfaceInfo]:
        """
        刷新指定接口的信息
        
        Args:
            interface_name: 接口名称
            
        Returns:
            更新后的接口信息
        """
        return self._get_interface_info(interface_name)
    
    def is_interface_available_for_capture(self, interface_name: str) -> bool:
        """
        检查接口是否可用于数据包捕获
        
        Args:
            interface_name: 接口名称
            
        Returns:
            是否可用于捕获
        """
        info = self.get_interface_by_name(interface_name)
        if not info:
            return False
        
        # 回环接口通常可以捕获
        if info.is_loopback:
            return True
        
        # 其他接口需要是活动状态
        return info.is_up and (info.ip_address is not None or info.mac_address is not None)