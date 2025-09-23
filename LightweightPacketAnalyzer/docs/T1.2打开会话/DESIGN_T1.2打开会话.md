# T1.2 打开会话功能 - 架构设计文档

## 文档信息
- **任务**: T1.2 打开会话功能
- **阶段**: Architect (架构设计)
- **创建时间**: 2024-12-19
- **基于文档**: ALIGNMENT_T1.2打开会话.md

## 1. 整体架构设计

### 1.1 系统架构图

```plantuml
@startuml T1.2_Architecture
!theme plain

package "GUI层" {
  [MainWindow] as MW
  [SessionDialog] as SD
}

package "业务逻辑层" {
  [SessionManager] as SM
  [DataLoader] as DL
  [GUIUpdater] as GU
}

package "数据访问层" {
  [DataManager] as DM
  [DataProcessor] as DP
}

package "数据存储层" {
  database "SQLite" {
    [sessions表] as ST
    [packets表] as PT
    [statistics表] as STAT
  }
}

MW --> SM : 调用打开会话
SM --> SD : 显示会话选择对话框
SD --> SM : 返回选中会话ID
SM --> DL : 加载会话数据
DL --> DM : 查询数据库
DM --> ST : 获取会话信息
DM --> PT : 获取数据包
DM --> STAT : 获取统计信息
DL --> GU : 传递加载的数据
GU --> MW : 更新GUI组件
GU --> DP : 更新数据处理器状态

@enduml
```

### 1.2 分层设计

#### GUI层 (Presentation Layer)
- **MainWindow**: 主窗口，提供用户交互入口
- **SessionDialog**: 会话选择对话框，显示会话列表

#### 业务逻辑层 (Business Logic Layer)
- **SessionManager**: 会话管理器，协调整个打开会话流程
- **DataLoader**: 数据加载器，负责从数据库加载会话相关数据
- **GUIUpdater**: GUI更新器，负责更新界面组件状态

#### 数据访问层 (Data Access Layer)
- **DataManager**: 数据管理器，提供数据库访问接口
- **DataProcessor**: 数据处理器，管理统计信息和状态

#### 数据存储层 (Data Storage Layer)
- **SQLite数据库**: 存储会话、数据包和统计信息

## 2. 核心组件设计

### 2.1 会话选择对话框 (SessionDialog)

#### 组件职责
- 显示历史会话列表
- 提供会话选择界面
- 支持取消操作

#### 设计规范
```plantuml
@startuml SessionDialog_Design
!theme plain

class SessionDialog {
  - parent: tk.Toplevel
  - sessions: List[Dict]
  - selected_session_id: Optional[int]
  
  + __init__(parent, sessions)
  + show() -> Optional[int]
  - _create_widgets()
  - _populate_session_list()
  - _on_session_select()
  - _on_ok_click()
  - _on_cancel_click()
}

@enduml
```

#### 界面布局
- 会话列表：显示会话名称、创建时间、数据包数量、总字节数
- 按钮区域：确定、取消按钮
- 排序方式：按创建时间倒序排列

### 2.2 数据加载器 (DataLoader)

#### 组件职责
- 根据会话ID加载相关数据
- 处理数据加载异常
- 提供加载进度反馈

#### 设计规范
```plantuml
@startuml DataLoader_Design
!theme plain

class DataLoader {
  - data_manager: DataManager
  - logger: Logger
  
  + load_session_data(session_id: int) -> SessionData
  + load_session_packets(session_id: int) -> List[Dict]
  + load_session_statistics(session_id: int) -> Dict
  - _validate_session_id(session_id: int) -> bool
  - _handle_load_error(error: Exception)
}

class SessionData {
  + session_info: Dict
  + packets: List[Dict]
  + statistics: Dict
  + packet_count: int
  + total_bytes: int
}

DataLoader --> SessionData : 创建

@enduml
```

### 2.3 GUI更新器 (GUIUpdater)

#### 组件职责
- 更新数据包列表显示
- 更新统计信息显示
- 更新会话状态和窗口标题
- 重置GUI组件状态

#### 设计规范
```plantuml
@startuml GUIUpdater_Design
!theme plain

class GUIUpdater {
  - main_window: MainWindow
  - logger: Logger
  
  + update_packet_list(packets: List[Dict])
  + update_statistics_display(stats: Dict)
  + update_session_status(session_info: Dict)
  + clear_current_display()
  - _populate_packet_tree(packets: List[Dict])
  - _format_statistics_text(stats: Dict) -> str
  - _update_window_title(session_name: str)
}

@enduml
```

## 3. 接口契约定义

### 3.1 主要接口规范

#### SessionManager接口
```python
class SessionManager:
    def open_session(self) -> bool:
        """
        打开会话主流程
        
        Returns:
            bool: 操作成功返回True，失败或取消返回False
        """
        pass
    
    def _check_current_state(self) -> str:
        """
        检查当前状态
        
        Returns:
            str: 'continue' | 'cancel'
        """
        pass
    
    def _show_session_selection(self) -> Optional[int]:
        """
        显示会话选择对话框
        
        Returns:
            Optional[int]: 选中的会话ID，取消返回None
        """
        pass
```

#### DataLoader接口
```python
class DataLoader:
    def load_session_data(self, session_id: int) -> SessionData:
        """
        加载会话完整数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            SessionData: 会话数据对象
            
        Raises:
            SessionNotFoundError: 会话不存在
            DataLoadError: 数据加载失败
        """
        pass
```

#### GUIUpdater接口
```python
class GUIUpdater:
    def update_with_session_data(self, session_data: SessionData) -> None:
        """
        使用会话数据更新GUI
        
        Args:
            session_data: 会话数据对象
        """
        pass
```

### 3.2 数据结构定义

#### SessionData数据结构
```python
@dataclass
class SessionData:
    session_info: Dict[str, Any]  # 会话基本信息
    packets: List[Dict[str, Any]]  # 数据包列表
    statistics: Dict[str, Any]     # 统计信息
    
    @property
    def session_id(self) -> int:
        return self.session_info['id']
    
    @property
    def session_name(self) -> str:
        return self.session_info['session_name']
    
    @property
    def packet_count(self) -> int:
        return len(self.packets)
```

## 4. 数据流向设计

### 4.1 主要数据流

```plantuml
@startuml DataFlow
!theme plain

actor User
participant MainWindow as MW
participant SessionManager as SM
participant SessionDialog as SD
participant DataLoader as DL
participant DataManager as DM
participant GUIUpdater as GU

User -> MW: 点击"打开会话"
MW -> SM: open_session()

SM -> SM: _check_current_state()
note right: 检查捕获状态\n询问保存当前数据

SM -> DM: get_sessions()
DM -> SM: sessions_list

SM -> SD: show(sessions_list)
SD -> User: 显示会话选择对话框
User -> SD: 选择会话
SD -> SM: selected_session_id

SM -> DL: load_session_data(session_id)
DL -> DM: 查询会话信息
DL -> DM: 查询数据包列表
DL -> DM: 查询统计信息
DM -> DL: 返回数据
DL -> SM: SessionData

SM -> GU: update_with_session_data(session_data)
GU -> MW: 更新数据包列表
GU -> MW: 更新统计信息
GU -> MW: 更新会话状态

SM -> MW: 操作完成
MW -> User: 显示成功消息

@enduml
```

### 4.2 异常处理流

```plantuml
@startuml ExceptionFlow
!theme plain

participant SessionManager as SM
participant DataLoader as DL
participant DataManager as DM
participant User

SM -> DL: load_session_data(session_id)

alt 会话不存在
    DL -> DM: 查询会话
    DM -> DL: 空结果
    DL -> SM: SessionNotFoundError
    SM -> User: 显示"会话不存在"错误
    
else 数据库连接失败
    DL -> DM: 查询数据
    DM -> DL: DatabaseError
    DL -> SM: DataLoadError
    SM -> User: 显示"数据加载失败"错误
    
else 数据损坏
    DL -> DM: 查询数据
    DM -> DL: 返回不完整数据
    DL -> DL: 数据验证失败
    DL -> SM: DataCorruptionError
    SM -> User: 显示"数据损坏"警告
    SM -> User: 询问是否继续加载
end

@enduml
```

## 5. 模块依赖关系

### 5.1 依赖关系图

```plantuml
@startuml Dependencies
!theme plain

package "T1.2打开会话" {
  [SessionManager]
  [SessionDialog]
  [DataLoader]
  [GUIUpdater]
}

package "现有模块" {
  [MainWindow]
  [DataManager]
  [DataProcessor]
}

package "标准库" {
  [tkinter]
  [logging]
  [typing]
}

SessionManager --> MainWindow : 集成到
SessionManager --> DataLoader : 使用
SessionManager --> GUIUpdater : 使用
SessionManager --> SessionDialog : 使用

DataLoader --> DataManager : 依赖
GUIUpdater --> MainWindow : 更新
GUIUpdater --> DataProcessor : 更新状态

SessionDialog --> tkinter : 使用
SessionManager --> logging : 使用

@enduml
```

### 5.2 集成点分析

#### 与MainWindow的集成
- **集成位置**: `main_window.py`中的`_open_session()`方法
- **集成方式**: 替换现有占位符实现
- **状态同步**: 更新`current_session_id`和`current_session_name`属性

#### 与DataManager的集成
- **使用接口**: `get_sessions()`, `get_packets()`, 现有统计查询方法
- **数据格式**: 复用现有数据结构，无需修改

#### 与DataProcessor的集成
- **状态更新**: 重置统计信息，更新当前会话状态
- **数据同步**: 确保统计信息与加载的数据一致

## 6. 性能和安全考虑

### 6.1 性能优化策略
- **数据分页**: 对于大量数据包，考虑分页加载
- **异步加载**: 使用后台线程加载数据，避免界面冻结
- **缓存机制**: 缓存会话列表，减少数据库查询

### 6.2 安全考虑
- **输入验证**: 验证会话ID的有效性
- **异常处理**: 完善的错误处理和用户提示
- **数据完整性**: 验证加载数据的完整性和一致性

## 7. 测试策略

### 7.1 单元测试覆盖
- SessionManager各方法的单元测试
- DataLoader数据加载逻辑测试
- GUIUpdater界面更新逻辑测试
- SessionDialog用户交互测试

### 7.2 集成测试
- 完整的打开会话流程测试
- 异常情况处理测试
- 与现有功能的兼容性测试

## 8. 下一步行动

### 8.1 进入Atomize阶段
- 基于此架构设计，拆分具体的原子任务
- 定义每个任务的输入输出契约
- 确定任务间的依赖关系

### 8.2 关键实现要点
- 优先实现SessionManager核心流程
- 重点关注与现有代码的集成
- 确保异常处理的完整性

---

**文档状态**: ✅ 架构设计完成  
**下一阶段**: Atomize - 原子任务拆分  
**预计完成时间**: 架构设计已完成，可进入下一阶段