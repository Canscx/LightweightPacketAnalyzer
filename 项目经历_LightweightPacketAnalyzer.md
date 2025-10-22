# 项目经历｜Lightweight Packet Analyzer（轻量级网络数据包分析器）

## 精简版（适合一页简历）
- 项目简介：基于 Python 的网络抓包与统计分析工具，支持会话管理、协议统计、流量趋势可视化、报告生成与主题切换。
- 个人职责：核心模块开发与维护，完善统计分析、图表生成与数据持久化；修复测试与质量问题，优化 GUI 体验与文档体系。
- 关键成果：
  - 实现协议分布、Top 协议、仪表盘等图表生成与导出（`reports/charts`）。
  - 完成新建/打开/保存会话功能与 CSV 导出，建立日志与数据库持久化。
  - 集成 ttkbootstrap 主题系统、字体与 GUI 兼容性优化，完善单元测试覆盖核心模块。
- 技术栈：Python、SQLite、Tkinter/ttkbootstrap、环境配置（.env）、pytest（或 unittest）、图表/报告导出。
- 代表模块与文件：`LightweightPacketAnalyzer/src/network_analyzer/statistics/protocol_statistics.py`（协议统计）；`tests/`（测试）；`logs/network_analyzer.log`（日志）；`network_analyzer.db`（数据库）。

---

## 详细版（适合作品集或技术型简历）
### 项目概述
- Lightweight Packet Analyzer 是一个用于抓取与分析网络流量的轻量级工具，包含会话管理、协议统计、流量趋势展示与报告生成，提供 GUI 交互与主题切换，适用于课程设计与实际网络分析场景。
- 项目路径：`d:\项目\计算机网络课设\LightweightPacketAnalyzer`

### 我的职责与贡献
- 作为核心开发者，负责统计分析、图表生成、数据持久化、GUI 体验优化以及测试修复。
- 推进需求设计与验收文档落地（`docs/` 中的 GUI 集成、协议统计、流量趋势、报告生成等）。
- 完善工程化实践：依赖管理（`pyproject.toml`）、环境配置（`.env/.env.example`）、日志记录（`logs/`）、数据库持久化（SQLite）。

### 核心功能
- 会话管理：新建、打开与保存会话（`docs/T1.1新建会话`、`T1.2打开会话`、`T1.3保存会话`）。
- 协议统计：统计协议分布、Top 协议，生成饼图/柱状图/仪表盘并导出图片（`reports/charts/`）。
- 流量趋势：按时间窗口统计与展示网络流量变化（`test_traffic_trends.py`、`test_traffic_trends.db`）。
- 数据导出：支持 CSV 导出与报告生成（`test_csv_export_fix.py`、`docs/生成报告`）。
- GUI 与主题：集成 Tkinter/ttkbootstrap，支持主题切换与界面优化（`docs/ttkbootstrap主题切换`）。
- 日志与存储：统一日志输出（`logs/network_analyzer.log`），SQLite 数据库持久化（`network_analyzer.db`）。

### 技术选型与架构
- 语言与框架：Python（标准库 + 第三方库），GUI 采用 Tkinter + ttkbootstrap。
- 存储与配置：SQLite（网络数据与统计指标存储），`.env` 环境配置。
- 报告与图表：生成协议饼图、Top 协议柱状图、仪表盘等图表图片文件（`reports/charts`）。
- 测试与质量：`tests/` 与多项 `test_*.py` 用例，覆盖捕获、分析、GUI、存储与配置等模块。

### 难点与解决方案
- 图表生成与配置一致性：针对图表主题、字体与布局的兼容性，修复 ChartConfig 与字体渲染问题（`test_chart_fix.py`、`test_font_fix.py`），确保报告在不同主题/字体下展示一致。
- 重复数据与会话一致性：通过 `test_duplicate_fix.py` 与会话相关测试，定位并修复重复数据或会话状态问题，确保持久化与加载流程稳定。
- GUI 启动与主题切换体验：优化主题系统（`docs/ttkbootstrap主题切换`），解决界面启动与主题切换时的样式闪烁与兼容问题。

### 质量保障与交付
- 单元测试：`tests/` 与根目录下的多项 `test_*.py` 用例，覆盖核心功能与已知缺陷修复。
- 日志与自检：提供多类 `debug_*` 脚本与日志系统，支持定位问题与回归验证（如 `debug_gui_startup.py`、`debug_packets.py`）。
- 文档与验收：配套设计、任务与验收文档，覆盖协议统计、流量趋势与 GUI 集成等模块（`docs/`）。

### 项目产出与可见成果
- 报告与图表：已生成的图表图片示例位于 `reports/charts/`（`protocol_pie_*.png`、`top_protocols_*.png`、`dashboard_*.png`）。
- 数据库：`network_analyzer.db` 与若干 `test_*.db`。
- 演示素材：`演示/`（示例 CSV）、《演示视频（带字幕）.mp4》。

### 关键词与加分项
- 关键词：网络抓包与分析、协议统计、流量趋势、GUI 主题切换、报告生成、SQLite 持久化、环境配置与日志、单元测试与质量保障。
- 加分项：完善的文档与测试体系、可视化报告导出、GUI 主题系统与用户体验优化。

---

## 可直接复制到简历的条目示例（中文）
Lightweight Packet Analyzer（轻量级网络数据包分析器）｜Python/SQLite/Tkinter
- 开发基于 Python 的网络抓包与分析工具，支持会话管理、协议统计、流量趋势与报告导出；集成 Tkinter/ttkbootstrap 主题系统，优化 GUI 体验与字体兼容。
- 负责协议统计与图表生成（饼图/柱状图/仪表盘），实现数据持久化与日志记录；完善单元测试覆盖核心模块并修复若干历史缺陷。
- 交付多份可视化报告与演示（`reports/charts`），配套设计与验收文档（`docs/`），提供 `.env` 配置与 `pyproject` 管理依赖，保证跨环境可复用与稳定性。