# Windows 系统巡检工具 (Flet GUI版)

一键采集 Windows 系统 27 项巡检数据，生成专业 HTML 报告。

## 功能特性

- 🖥️ **4 页面概览**：概览仪表盘 / 硬件网络 / 安全用户 / 进程软件
- 📊 **27 项巡检数据**：CPU、内存、磁盘、网络、安全、用户、进程、软件等
- 📄 **HTML 报告导出**：一键生成可分享的专业报告
- 🎨 **深色主题界面**：现代卡片式 UI
- 📦 **Windows exe 打包**：通过 GitHub Actions 自动构建

## 快速开始

### 本地运行
```bash
pip install -r requirements.txt
python main.py
```

### 构建 exe
```bash
pip install flet
flet pack main.py --name WindowsInspector
```

## GitHub Actions 构建

推送代码后会自动在 Windows Runner 上构建 .exe：
- push 到 main 分支 → 自动构建
- 发布 Release → 自动上传附件

## 4 页面说明

| 页面 | 内容 |
|------|------|
| 概览 | 风险等级、CPU/内存/磁盘状态、风险告警 |
| 硬件网络 | CPU/GPU、内存芯片、磁盘、网络适配器、IP配置、共享 |
| 安全用户 | 防火墙、RDP、BitLocker、Defender、用户与权限 |
| 进程软件 | 进程Top10、启动项、计划任务、软件列表、补丁 |

## 技术栈

- **Python 3.11+**
- **Flet** (Flutter-style GUI)
- **GitHub Actions** (Windows CI/CD)
