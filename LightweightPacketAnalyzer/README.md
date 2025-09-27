# 网络流量统计系统 (Network Traffic Analyzer)

## 项目简介

这是一个轻量级的网络数据包分析器，用于计算机网络课程设计。该系统能够捕获、分析和统计网络流量数据，并提供直观的图形界面展示结果。

## 功能特性

- 🔍 **数据包捕获**: 实时捕获网络数据包
- 📊 **流量统计**: 统计各种网络协议的流量分布
- 📈 **数据可视化**: 提供图表展示流量趋势
- 🖥️ **图形界面**: 用户友好的GUI界面
- 💾 **数据存储**: 支持数据的保存和加载
- ⚙️ **配置管理**: 灵活的配置选项

## 系统要求

- Python 3.8+
- Windows/Linux/macOS
- 管理员权限（用于数据包捕获）

## 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd LightweightPacketAnalyzer
```

### 2. 创建虚拟环境
```bash
python -m venv venv

# Windows
.\\venv\\Scripts\\activate

# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -e .
```

### 4. 开发环境安装
```bash
pip install -e .[dev]
```

## 使用方法

### 命令行启动
```bash
network-analyzer
```

### Python模块启动
```python
from network_analyzer.main import main
main()
```

## 项目结构

```
LightweightPacketAnalyzer/
├── src/
│   └── network_analyzer/
│       ├── __init__.py
│       ├── main.py
│       ├── capture/
│       │   ├── __init__.py
│       │   └── packet_capture.py
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── traffic_analyzer.py
│       │   └── statistics.py
│       ├── storage/
│       │   ├── __init__.py
│       │   └── data_manager.py
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   └── components/
│       └── config/
│           ├── __init__.py
│           └── settings.py
├── tests/
├── docs/
├── data/
├── .env.example
├── pyproject.toml
└── README.md
```

## 开发指南

### 运行测试
```bash
pytest
```

### 代码格式化
```bash
black src/ tests/
```

### 类型检查
```bash
mypy src/
```

## 配置说明

复制 `.env.example` 到 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 联系方式

- 项目维护者: GUO HUAN
- 邮箱: 743278331@qq.com

## 更新日志

### v2.0 (当前版本)
- 更新开发者信息
- 完善使用说明文档
- 优化用户界面体验
- 增强会话管理功能
- 改进数据导出功能

### v0.1.0
- 初始版本发布
- 基础数据包捕获功能
- 简单的流量统计
- 基本GUI界面