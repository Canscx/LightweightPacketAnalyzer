# 网络流量统计分析工具 - 系统架构设计

## 1. 整体架构设计

### 1.1 系统架构图

```plantuml
@startuml
!define RECTANGLE class

package "网络流量统计分析工具" {
    
    package "用户界面层 (UI Layer)" {
        RECTANGLE MainWindow {
            +start_capture()
            +stop_capture()
            +update_display()
            +export_data()
        }
        
        RECTANGLE ControlPanel {
            +refresh_interval_selector
            +network_interface_selector
            +start_stop_button
        }
        
        RECTANGLE StatisticsDisplay {
            +ip_statistics_table
            +traffic_chart
            +status_bar
        }
    }
    
    package "业务逻辑层 (Business Layer)" {
        RECTANGLE PacketCapture {
            +start_sniffing()
            +stop_sniffing()
            +filter_packets()
            +get_network_interfaces()
        }
        
        RECTANGLE DataProcessor {
            +process_packet()
            +update_statistics()
            +calculate_traffic()
            +get_statistics()
        }
        
        RECTANGLE DataManager {
            +store_packet_info()
            +get_ip_statistics()
            +export_to_csv()
            +reset_statistics()
        }
    }
    
    package "数据访问层 (Data Layer)" {
        RECTANGLE StatisticsStorage {
            +ip_packet_count: dict
            +ip_traffic_size: dict
            +packet_history: list
            +start_time: datetime
        }
    }
    
    package "外部依赖 (External Dependencies)" {
        RECTANGLE ScapyLibrary {
            +sniff()
            +get_if_list()
            +packet parsing
        }
        
        RECTANGLE TkinterGUI {
            +widgets
            +event handling
            +threading
        }
        
        RECTANGLE MatplotlibChart {
            +plot generation
            +real-time updates
            +chart embedding
        }
    }
}

' 关系定义
MainWindow --> ControlPanel
MainWindow --> StatisticsDisplay
MainWindow --> PacketCapture
MainWindow --> DataProcessor

PacketCapture --> ScapyLibrary
DataProcessor --> DataManager
DataManager --> StatisticsStorage

StatisticsDisplay --> MatplotlibChart
MainWindow --> TkinterGUI

PacketCapture --> DataProcessor : packet_data
DataProcessor --> StatisticsDisplay : statistics_data
ControlPanel --> PacketCapture : control_commands

@enduml
```

### 1.2 分层设计说明

#### 用户界面层 (UI Layer)
- **MainWindow**: 主窗口控制器，协调各个UI组件
- **ControlPanel**: 控制面板，包含开始/停止按钮、刷新频率选择等
- **StatisticsDisplay**: 统计数据展示区域，包含表格和图表

#### 业务逻辑层 (Business Layer)
- **PacketCapture**: 数据包捕获模块，封装Scapy抓包功能
- **DataProcessor**: 数据处理模块，解析和统计数据包信息
- **DataManager**: 数据管理模块，负责数据存储和导出

#### 数据访问层 (Data Layer)
- **StatisticsStorage**: 统计数据存储，使用内存数据结构

## 2. 核心模块设计

### 2.1 数据包捕获模块 (PacketCapture)

```plantuml
@startuml
class PacketCapture {
    -interface: str
    -is_capturing: bool
    -packet_filter: str
    -callback_function: callable
    
    +__init__(interface: str, callback: callable)
    +start_sniffing(): void
    +stop_sniffing(): void
    +set_filter(filter_str: str): void
    +get_available_interfaces(): list
    -packet_handler(packet): void
}

note right of PacketCapture::start_sniffing
    使用Scapy的sniff()函数
    在独立线程中运行
    应用数据包过滤器
end note

note right of PacketCapture::packet_handler
    解析数据包基本信息
    调用回调函数传递数据
    处理异常情况
end note
@enduml
```

### 2.2 数据处理模块 (DataProcessor)

```plantuml
@startuml
class DataProcessor {
    -data_manager: DataManager
    -packet_count: int
    -start_time: datetime
    
    +__init__(data_manager: DataManager)
    +process_packet(packet_info: dict): void
    +get_current_statistics(): dict
    +reset_statistics(): void
    +calculate_traffic_rate(): float
    -extract_packet_info(packet): dict
    -update_ip_statistics(src_ip: str, packet_size: int): void
}

note right of DataProcessor::process_packet
    提取源IP地址
    计算数据包大小
    更新统计信息
    记录时间戳
end note

note right of DataProcessor::extract_packet_info
    支持TCP、UDP、ICMP协议
    提取IP层信息
    计算有效载荷大小
end note
@enduml
```

### 2.3 用户界面模块 (MainWindow)

```plantuml
@startuml
class MainWindow {
    -root: tk.Tk
    -packet_capture: PacketCapture
    -data_processor: DataProcessor
    -control_panel: ControlPanel
    -statistics_display: StatisticsDisplay
    -update_timer: str
    
    +__init__()
    +setup_ui(): void
    +start_capture(): void
    +stop_capture(): void
    +update_display(): void
    +on_refresh_interval_changed(interval: int): void
    +export_statistics(): void
    -schedule_update(): void
}

note right of MainWindow::update_display
    获取最新统计数据
    更新表格显示
    刷新图表
    更新状态栏
end note

note right of MainWindow::schedule_update
    使用tkinter.after()
    根据用户选择的频率
    定时调用update_display()
end note
@enduml
```

## 3. 数据流设计

### 3.1 数据流向图

```plantuml
@startuml
!define RECTANGLE class

start
:网络数据包;
:Scapy捕获数据包;
:PacketCapture过滤处理;
:DataProcessor解析统计;
:DataManager存储数据;
:StatisticsDisplay展示;
:用户界面更新;
stop

note right
    数据流经过以下阶段：
    1. 网络层捕获
    2. 协议层解析
    3. 业务层统计
    4. 存储层管理
    5. 展示层渲染
end note
@enduml
```

### 3.2 实时更新机制

```plantuml
@startuml
participant "MainWindow" as MW
participant "PacketCapture" as PC
participant "DataProcessor" as DP
participant "StatisticsDisplay" as SD

MW -> PC: start_sniffing()
activate PC

loop 数据包捕获
    PC -> DP: process_packet(packet_info)
    activate DP
    DP -> DP: update_statistics()
    deactivate DP
end

loop 定时更新 (用户选择频率)
    MW -> DP: get_current_statistics()
    activate DP
    DP --> MW: statistics_data
    deactivate DP
    
    MW -> SD: update_display(statistics_data)
    activate SD
    SD -> SD: refresh_table()
    SD -> SD: update_chart()
    deactivate SD
end

MW -> PC: stop_sniffing()
deactivate PC
@enduml
```

## 4. 接口契约定义

### 4.1 数据包信息接口

```python
# 数据包信息数据结构
PacketInfo = {
    'timestamp': datetime,      # 捕获时间戳
    'src_ip': str,             # 源IP地址
    'dst_ip': str,             # 目标IP地址
    'protocol': str,           # 协议类型 (TCP/UDP/ICMP)
    'packet_size': int,        # 数据包大小(字节)
    'src_port': int,           # 源端口(可选)
    'dst_port': int            # 目标端口(可选)
}
```

### 4.2 统计数据接口

```python
# 统计数据结构
StatisticsData = {
    'ip_statistics': {
        'ip_address': {
            'packet_count': int,    # 数据包数量
            'total_bytes': int,     # 总流量字节数
            'protocols': dict,      # 协议分布
            'first_seen': datetime, # 首次出现时间
            'last_seen': datetime   # 最后出现时间
        }
    },
    'global_stats': {
        'total_packets': int,       # 总数据包数
        'total_bytes': int,         # 总流量
        'unique_ips': int,          # 唯一IP数量
        'capture_duration': float,  # 捕获时长(秒)
        'packets_per_second': float # 每秒数据包数
    }
}
```

### 4.3 配置参数接口

```python
# 配置参数结构
ConfigParams = {
    'network_interface': str,       # 网络接口名称
    'packet_filter': str,          # 数据包过滤器
    'refresh_interval': int,       # 刷新间隔(秒)
    'max_ip_entries': int,         # 最大IP条目数
    'enable_export': bool,         # 是否启用导出功能
    'chart_type': str             # 图表类型
}
```

## 5. 异常处理策略

### 5.1 异常分类和处理

```plantuml
@startuml
!define EXCEPTION class

package "异常处理体系" {
    EXCEPTION NetworkException {
        +interface_not_found
        +permission_denied
        +network_unreachable
    }
    
    EXCEPTION PacketException {
        +malformed_packet
        +unsupported_protocol
        +parsing_error
    }
    
    EXCEPTION UIException {
        +widget_error
        +display_error
        +user_input_error
    }
    
    EXCEPTION DataException {
        +storage_full
        +export_failed
        +data_corruption
    }
}

note right of NetworkException
    网络相关异常处理：
    - 检查网络接口可用性
    - 提示权限问题
    - 提供备选接口
end note

note right of PacketException
    数据包处理异常：
    - 跳过无法解析的包
    - 记录错误日志
    - 继续处理后续包
end note
@enduml
```

### 5.2 错误恢复机制

1. **网络接口错误**: 自动切换到可用接口
2. **权限不足**: 提示用户以管理员身份运行
3. **内存不足**: 实现数据清理和限制机制
4. **UI响应超时**: 在独立线程中处理耗时操作

## 6. 性能优化设计

### 6.1 性能关键点

1. **数据包处理**: 使用异步处理避免阻塞UI
2. **内存管理**: 限制统计数据条目数量
3. **UI更新**: 批量更新减少重绘频率
4. **数据结构**: 使用高效的字典和列表操作

### 6.2 资源限制

- **最大IP条目**: 1000个
- **历史数据保留**: 最近1小时
- **UI更新频率**: 最快1秒
- **内存使用限制**: 100MB

## 7. 扩展性设计

### 7.1 协议扩展接口

```python
class ProtocolParser:
    def can_parse(self, packet) -> bool:
        """判断是否能解析该协议"""
        pass
    
    def parse_packet(self, packet) -> PacketInfo:
        """解析数据包信息"""
        pass
    
    def get_protocol_name(self) -> str:
        """获取协议名称"""
        pass
```

### 7.2 可视化扩展接口

```python
class ChartRenderer:
    def render(self, data: StatisticsData) -> None:
        """渲染图表"""
        pass
    
    def update(self, data: StatisticsData) -> None:
        """更新图表数据"""
        pass
    
    def get_chart_type(self) -> str:
        """获取图表类型"""
        pass
```

---

**文档状态**: 架构设计完成  
**创建时间**: 2024年1月  
**版本**: v1.0  
**下一步**: 进入Atomize阶段，拆分开发任务