# 🌐 Lightweight Packet Analyzer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/yourusername/LightweightPacketAnalyzer)

> 一个功能完整的轻量级网络数据包分析器，专为计算机网络课程设计和网络学习而开发。

## ✨ 项目简介

Lightweight Packet Analyzer 是一个基于 Python 开发的网络流量统计与分析系统，提供实时数据包捕获、协议解析、流量统计和可视化展示功能。该项目采用现代化的 GUI 设计，支持多种主题切换，适用于网络教学、故障诊断和性能监控场景。

### 🎯 设计目标

- **教育友好**: 直观展示网络协议栈工作原理
- **轻量高效**: 低资源占用，高性能数据处理
- **功能完整**: 从数据捕获到报告生成的完整流程
- **易于使用**: 现代化 GUI 界面，操作简单直观

## 🚀 核心功能

### 📡 数据包捕获与解析
- **实时捕获**: 支持多网络接口选择和 BPF 过滤器
- **协议解析**: 深度解析以太网、ARP、IPv4/IPv6、TCP、UDP、ICMP 协议
- **数据展示**: 实时数据包列表显示，支持详情查看和十六进制转储

### 📊 统计分析与可视化
- **协议统计**: 协议分布统计，Top IP/端口分析
- **流量趋势**: 时间序列流量趋势分析
- **图表生成**: 饼图、柱状图、仪表盘等多种图表类型
- **数据导出**: 支持 PNG、CSV、PDF 格式导出

### 💾 会话管理
- **会话控制**: 新建、保存、加载会话功能
- **数据持久化**: SQLite 数据库存储，支持历史数据查询
- **配置管理**: 灵活的 .env 配置文件支持

### 🎨 用户界面
- **现代化 GUI**: 基于 ttkbootstrap 的现代化界面设计
- **主题切换**: 支持多种主题风格切换
- **响应式布局**: 自适应窗口大小调整

## 🛠️ 技术栈

| 技术领域 | 使用技术 |
|---------|---------|
| **核心语言** | Python 3.8+ |
| **网络库** | Scapy (数据包捕获与解析) |
| **GUI框架** | Tkinter + ttkbootstrap |
| **数据可视化** | Matplotlib |
| **数据处理** | Pandas, NumPy |
| **数据存储** | SQLite |
| **报告生成** | ReportLab (PDF), Jinja2 (HTML) |
| **配置管理** | python-dotenv |
| **测试框架** | pytest |

## 📋 系统要求

- **操作系统**: Windows 10+, Linux, macOS
- **Python版本**: 3.8 或更高版本
- **权限要求**: 管理员权限（用于网络数据包捕获）
- **内存要求**: 最少 512MB 可用内存
- **存储空间**: 至少 100MB 可用空间

## 🔧 安装指南

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/LightweightPacketAnalyzer.git
cd LightweightPacketAnalyzer
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖
```bash
# 安装项目依赖
pip install -e .

# 开发环境安装（包含测试工具）
pip install -e .[dev]
```

## 🚀 快速开始

### 启动应用程序
```bash
# 进入项目目录
cd LightweightPacketAnalyzer

# 启动主程序（需要管理员权限）
python src/network_analyzer/main.py

# 或使用命令行参数
python src/network_analyzer/main.py --config custom_config.env
```

### 基本使用流程

1. **选择网络接口**: 启动后选择要监听的网络接口
2. **设置过滤器**: 可选设置 BPF 过滤器（如 `tcp port 80`）
3. **开始捕获**: 点击开始按钮进行数据包捕获
4. **查看统计**: 实时查看协议分布和流量统计
5. **生成报告**: 导出分析报告和图表

## 📸 功能截图

### 主界面
- 实时数据包列表显示
- 协议统计饼图
- 流量趋势图表

### 统计分析
- 协议分布统计
- Top IP 地址分析
- 端口使用情况

### 报告生成
- PDF 格式报告
- CSV 数据导出
- 图表图片保存

## 🏗️ 项目架构

```
LightweightPacketAnalyzer/
├── src/network_analyzer/          # 主要源代码
│   ├── analysis/                  # 数据包分析模块
│   ├── capture/                   # 数据包捕获模块
│   ├── gui/                       # 图形界面模块
│   ├── processing/                # 数据处理模块
│   ├── reports/                   # 报告生成模块
│   ├── statistics/                # 统计分析模块
│   ├── storage/                   # 数据存储模块
│   └── utils/                     # 工具函数
├── tests/                         # 单元测试
├── docs/                          # 项目文档
├── reports/charts/                # 生成的图表
├── logs/                          # 日志文件
└── pyproject.toml                 # 项目配置
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试模块
pytest tests/test_capture.py

# 生成测试覆盖率报告
pytest --cov=network_analyzer --cov-report=html
```

### 测试覆盖
- 数据包捕获测试
- 协议解析测试
- GUI 功能测试
- 数据存储测试
- 统计分析测试

## 📚 使用文档

### 配置说明
项目使用 `.env` 文件进行配置，主要配置项包括：

```env
# 数据包捕获配置
CAPTURE_INTERFACE=auto              # 网络接口选择
CAPTURE_TIMEOUT=30                  # 捕获超时时间
CAPTURE_PACKET_COUNT=1000          # 最大捕获包数

# 数据存储配置
DATABASE_FILE=network_analyzer.db   # 数据库文件路径
DATA_DIRECTORY=./data              # 数据目录

# GUI配置
WINDOW_WIDTH=1200                  # 窗口宽度
WINDOW_HEIGHT=800                  # 窗口高度
THEME=default                      # 界面主题

# 日志配置
LOG_LEVEL=INFO                     # 日志级别
LOG_FILE=./logs/network_analyzer.log  # 日志文件路径
```

### BPF 过滤器示例
```bash
# 捕获 HTTP 流量
tcp port 80

# 捕获特定 IP 的流量
host 192.168.1.1

# 捕获 TCP 流量
tcp

# 捕获 UDP 流量
udp

# 组合过滤器
tcp and port 443
```

## 🤝 贡献指南

### 开发环境设置
1. Fork 项目到你的 GitHub 账户
2. 克隆你的 Fork 到本地
3. 创建新的功能分支
4. 进行开发和测试
5. 提交 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用 Black 进行代码格式化
- 添加适当的注释和文档字符串
- 编写单元测试覆盖新功能

### 提交规范
```bash
# 功能添加
git commit -m "feat: 添加新的协议解析功能"

# Bug 修复
git commit -m "fix: 修复数据包捕获内存泄漏问题"

# 文档更新
git commit -m "docs: 更新安装指南"
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Scapy](https://scapy.net/) - 强大的数据包处理库
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) - 现代化的 Tkinter 主题
- [Matplotlib](https://matplotlib.org/) - 数据可视化库
- 所有为项目做出贡献的开发者

## 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/yourusername/LightweightPacketAnalyzer)
- **问题反馈**: [Issues](https://github.com/yourusername/LightweightPacketAnalyzer/issues)
- **功能建议**: [Discussions](https://github.com/yourusername/LightweightPacketAnalyzer/discussions)

## 🔄 更新日志

### v2.0.0 (2025-01-XX)
- ✨ 新增主题切换功能
- 🐛 修复数据包重复显示问题
- 📊 改进统计图表生成
- 🔧 优化配置管理系统

### v1.0.0 (2024-XX-XX)
- 🎉 初始版本发布
- 📡 基础数据包捕获功能
- 📊 协议统计分析
- 🖥️ GUI 界面实现

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给它一个 Star！**

Made with ❤️ for Computer Network Course Design

</div>