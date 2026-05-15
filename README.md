# 👁️ ShadowScan (潜影)
> **Trace the Shadow, Link All Hidden Domains.** > 人生中第一个子域名扫描工具，不追求新意，存在本身就是它的意义。
>

<div align="center">

![Python](https://img.shields.io/badge/python-3.7+-blue.svg) ![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg) ![Status](https://img.shields.io/badge/status-Developing-orange.svg)
</div>

## 📖 简介 / Introduction

**ShadowScan (潜影)** ，一款简易的子域名发现与探活工具。

---

## ✨ 核心特性 / Features

- 🚀 **多线程加速 (Multi-threading)**：基于 `ThreadPoolExecutor` 实现并发请求，线程数可自定义，极大地缩短了扫描周期。
- 🎨 **视觉化输出**：采用 ANSI 转义码，对 200 (成功)、404 (缺失) 及其他状态码进行色彩区分，重要信息一目了然。
- 🔍 **双向状态过滤**：
  - `-s/--status`: 包含模式，仅查看你关心的状态码（如 200, 302）。
  - `-x/--exclude`: 排除模式，自动过滤掉噪音（如大量 404 或 403）。
  - `-ip`：ip显示，支持通过 `-ip` 参数实时查看子域名的 A 记录，快速定位目标基础设施。
- 🛡️ **健壮性优化**：
  - 线程安全：内置 `threading.Lock` 确保终端输出不乱序。
  - 优雅退出：支持 `Ctrl+C` 捕获，确保程序在退出时能安全释放资源。
  - 容错处理：针对超时、DNS 解析失败等网络异常做了详尽的捕获与提醒。
- 📂 **自动化持久化**：扫描结果自动按域名存放在 `URL/` 目录下，方便后续查阅。

---

## 🚀 快速开始 / Quick Start

### 1. 环境克隆

```bash
git clone https://github.com/SweetSour520/ShadowScan.git
cd ShadowScan
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行演示

```bash
# 基础运行
python ShadowScan.py

# 筛选 200 和 301 状态码
python ShadowScan.py -s 200,301

# 排除 404 状态码
python ShadowScan.py -x 404

# 显示 IP
python ShadowScan.py -ip
```

---

## 🛠️ 命令行参数 / Usage

| 参数 | 描述 | 示例 |
|------|------|------|
| `-h, --help` | 显示帮助信息 | `python ShadowScan.py -h` |
| `-s, --status` | 仅显示指定状态码的结果 | `-s 200,302` |
| `-x, --exclude` | 排除指定状态码的结果 | `-x 404,403` |
| `-ip, --show_ip` | 显示域名解析的 IP 地址 | `-ip` |


---

## 📅 路线图 / Roadmap

- [x] 多线程并发引擎
- [x] 动态状态码筛选
- [ ] 异步 IO (Asyncio) 探测模块引入
- [ ] 支持 favicon.ico Hash 识别（「幽瞳」系列联动功能）
- [ ] 导出扫描结果至 Excel 报表

---

## 🤝 贡献与致谢 / Acknowledgements

- **Author**: SweetSour ([@SweetSour520](https://www.google.com/search?q=https://github.com/SweetSour520))
- **Inspiration**: 灵感源自网安圈前辈的工具 - httpx、转子女神。

---

## 📄 免责声明 / Disclaimer

本工具仅用于合法合规的授权渗透测试、企业自验及安全教学。使用者因违反相关法律法规而导致的一切后果由使用者自行承担，作者不承担任何责任。

