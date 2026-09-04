<div align="center">

# ⚡ OptiFlow System Guardian
### *Autonomous Windows Flow Accelerator & Resource Guardian*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg?logo=windows)](https://microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dependencies: Zero](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![RAM Footprint: <15MB](https://img.shields.io/badge/RAM%20Footprint-%3C15MB-success.svg)]()

**OptiFlow** is a zero-dependency, ultra-lightweight Windows performance guardian designed specifically for high system loads, tight memory environments (8GB RAM), and hybrid processor architectures (such as **Intel 12th/13th/14th Gen P-Cores & E-Cores**).

</div>

---

## 🎯 The Problem It Solves

On modern Windows laptops running developer workflows (VS Code, Chrome/Edge, compilers, Python, deep learning/DSA scripts):
1. **Aggressive Pagefile Swapping**: When physical memory hits 85–95%, Windows starts paging to the SSD, resulting in micro-stutters, input lag, and slow application switching.
2. **Hybrid Core Competition**: Background bloat processes (telemetry, search indexers, update daemons) frequently steal cycles from the 2 high-performance **P-Cores**, starving foreground development tasks.
3. **Stale Memory Hoarding**: Idle background apps hold onto unneeded working sets instead of releasing them to physical RAM.

---

## ✨ Key Features

- **⚡ Intelligent Working Set Compaction**:
  - Leverages native Windows Win32 `psapi.EmptyWorkingSet` via `ctypes`.
  - Reclaims **500MB – 1.2GB of physical RAM** on demand or automatically without terminating apps.
- **🚀 Intel Thread Director Tuner**:
  - Automatically identifies active developer processes (`code.exe`, `g++.exe`, `python.exe`, `powershell.exe`, etc.) and raises priority to `ABOVE_NORMAL`, pinning them to the **P-Cores**.
  - Shifts background hogs to the **8 Efficient Cores (E-Cores)**.
- **🛡️ Autonomous Guardian Daemon**:
  - Monitors system state every 12 seconds with `< 0.05% CPU` usage.
  - Automatically triggers soft compaction whenever memory pressure hits 82%.
- **🧹 Cache & Zombie Purger**:
  - Cleans `%TEMP%` junk safely.
  - Reaps orphaned compiler instances (`g++.exe`, `ld.exe`) or abandoned workers.
- **🖥️ Interactive Cyber-Clean Dashboard**:
  - Real-time physical RAM usage gauge.
  - Live top 10 memory-consuming processes.
  - 1-click **Instant Turbo Boost**, **Purge Temp Cache**, and **Clear Stuck Workers**.
- **🪶 Zero Dependencies**:
  - Pure Python standard library & native Win32 APIs. No heavy pip packages required.

---

## 🚀 Quick Start

### 1. Run the Dashboard (Recommended)
Simply double-click:
```bat
run_optiflow.bat
```
Or run from terminal:
```bash
python optiflow_server.py
```
This automatically starts the guardian engine and opens your browser at **[http://localhost:5050](http://localhost:5050)**.

### 2. Standalone Background Guardian (CLI Mode)
If you prefer running only the background daemon in the terminal:
```bash
python optiflow_daemon.py
```

---

## 🏗️ Architecture

```
                      +-----------------------------+
                      |     OptiFlow Dashboard      |
                      |   (http://localhost:5050)   |
                      +--------------+--------------+
                                     |
                          HTTP REST API / WebSocket
                                     |
                      +--------------v--------------+
                      |      OptiFlow Server        |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                                             |
+-------------v---------------+             +---------------v-------------+
|    OptiFlow Daemon Loop     |             |      OptiFlow Core          |
|  - Threshold checks (>82%)  |             |  - psapi.EmptyWorkingSet    |
|  - Autonomous compaction    |             |  - SetPriorityClass (Win32) |
|  - Zombie task reaper       |             |  - Temp & Cache Cleaner     |
+-----------------------------+             +-----------------------------+
              |                                             |
              +----------------------+----------------------+
                                     |
                      +--------------v--------------+
                      |   Windows Kernel32 / Win32  |
                      |  - Intel P-Cores Priority   |
                      |  - Physical RAM Headroom    |
                      +-----------------------------+
```

---

## 🤖 Running Local AI Models on 8GB RAM

For guidelines on running local AI models (such as **Qwen 2.5 Coder 1.5B/3B** or **DeepSeek-R1 1.5B**) on 8GB RAM at 40–55 tokens/second without system lag, see:
- 📖 [**AI Model Hardware Guide**](ai_model_guide.md)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

Developed with ❤️ by **Devansh Ganatra**.
