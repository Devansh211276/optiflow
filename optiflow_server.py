"""
OptiFlow Web Server & Dashboard
Lightweight HTTP API + Cyber-Clean UI for real-time monitoring and flow control.
Zero external dependencies (uses standard library http.server).
"""

import os
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Ensure local imports work whether executed directly or as a package
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from optiflow_core import (
    get_memory_status,
    get_process_list,
    optimize_idle_memory,
    boost_dev_flow,
    clean_temp_cache,
    reap_zombies
)
from optiflow_daemon import daemon_instance

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OptiFlow // System Performance Guardian</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0a0d14;
            --bg-card: #101622;
            --bg-card-hover: #151d2d;
            --border-subtle: #1e293b;
            --accent-cyan: #06b6d4;
            --accent-glow: rgba(6, 182, 212, 0.25);
            --accent-purple: #8b5cf6;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --font-mono: 'JetBrains Mono', monospace;
            --font-sans: 'Plus Jakarta Sans', sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-sans);
            padding: 24px;
            min-height: 100vh;
            background-image: radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-subtle);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-logo {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 22px;
            color: #fff;
            box-shadow: 0 0 20px var(--accent-glow);
        }

        .brand-title h1 {
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #fff, var(--text-muted));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-title p {
            font-size: 13px;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }

        .system-pill {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--accent-emerald);
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-family: var(--font-mono);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-emerald);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        .grid-dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }

        .card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 20px;
            position: relative;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .card-header h3 {
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }

        .stat-value {
            font-size: 34px;
            font-weight: 800;
            color: #fff;
            line-height: 1.1;
        }

        .stat-sub {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 6px;
            font-family: var(--font-mono);
        }

        .progress-bar-bg {
            background-color: #1e293b;
            border-radius: 999px;
            height: 10px;
            overflow: hidden;
            margin-top: 14px;
        }

        .progress-bar-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            transition: width 0.5s ease;
        }

        .actions-panel {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }

        .btn-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 12px;
        }

        button {
            cursor: pointer;
            border: none;
            outline: none;
            padding: 12px 20px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 14px;
            font-family: var(--font-sans);
            display: inline-flex;
            align-items: center;
            gap: 10px;
            transition: all 0.2s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0284c7);
            color: #fff;
            box-shadow: 0 4px 14px var(--accent-glow);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
        }

        .btn-secondary {
            background: #1e293b;
            color: var(--text-main);
            border: 1px solid #334155;
        }

        .btn-secondary:hover {
            background: #334155;
            transform: translateY(-2px);
        }

        .btn-danger {
            background: rgba(244, 63, 94, 0.15);
            color: var(--accent-rose);
            border: 1px solid rgba(244, 63, 94, 0.3);
        }

        .btn-danger:hover {
            background: rgba(244, 63, 94, 0.25);
            transform: translateY(-2px);
        }

        .toggle-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 18px;
            background: #0d131f;
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
            margin-top: 10px;
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 48px;
            height: 26px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #334155;
            transition: .3s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .3s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--accent-cyan);
        }

        input:checked + .slider:before {
            transform: translateX(22px);
        }

        .data-section {
            display: grid;
            grid-template-columns: 3fr 2fr;
            gap: 20px;
        }

        .table-wrap {
            max-height: 380px;
            overflow-y: auto;
            border-radius: 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th {
            background-color: #0d131f;
            color: var(--text-muted);
            text-align: left;
            padding: 10px 14px;
            font-weight: 600;
            font-family: var(--font-mono);
            position: sticky;
            top: 0;
        }

        td {
            padding: 10px 14px;
            border-bottom: 1px solid #1e293b;
        }

        tr:hover td {
            background-color: #172033;
        }

        .badge-dev {
            background: rgba(139, 92, 246, 0.15);
            color: var(--accent-purple);
            border: 1px solid rgba(139, 92, 246, 0.3);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-family: var(--font-mono);
        }

        .badge-normal {
            background: rgba(148, 163, 184, 0.1);
            color: var(--text-muted);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-family: var(--font-mono);
        }

        .log-box {
            background-color: #090c13;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 14px;
            height: 380px;
            overflow-y: auto;
            font-family: var(--font-mono);
            font-size: 12px;
            color: #cbd5e1;
            line-height: 1.6;
        }

        .log-entry {
            margin-bottom: 6px;
            word-break: break-all;
        }

        .log-cyan { color: var(--accent-cyan); }
        .log-green { color: var(--accent-emerald); }
        .log-amber { color: var(--accent-amber); }

        /* Notification Toast */
        #toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #1e293b;
            color: #fff;
            border: 1px solid var(--accent-cyan);
            border-radius: 12px;
            padding: 14px 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            font-weight: 600;
            display: none;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="brand-logo">⚡</div>
                <div class="brand-title">
                    <h1>OptiFlow Bot</h1>
                    <p>Intel Core i5-1235U (10 Cores) // 8.0 GB RAM Architecture Guardian</p>
                </div>
            </div>
            <div class="system-pill">
                <div class="pulse-dot"></div>
                <span id="header-guardian-text">GUARDIAN ACTIVE</span>
            </div>
        </header>

        <!-- Metric Cards -->
        <div class="grid-dashboard">
            <div class="card">
                <div class="card-header">
                    <h3>Physical Memory</h3>
                    <span id="ram-badge" style="font-family: var(--font-mono); font-size: 13px; font-weight: 700;">--%</span>
                </div>
                <div class="stat-value" id="stat-ram-used">-- GB</div>
                <div class="stat-sub">of <span id="stat-ram-total">8.0</span> GB (<span id="stat-ram-avail">--</span> GB Free)</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="ram-bar" style="width: 0%;"></div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>Processor & Flow</h3>
                    <span style="color: var(--accent-purple); font-family: var(--font-mono); font-size: 12px; font-weight: 700;">THREAD DIRECTOR</span>
                </div>
                <div class="stat-value" style="font-size: 26px; color: var(--accent-cyan);">2 P-Cores + 8 E-Cores</div>
                <div class="stat-sub" id="p-core-status">Active Dev Apps Pinned to High Performance</div>
                <div class="progress-bar-bg" style="background: #1e1b4b;">
                    <div class="progress-bar-fill" style="width: 100%; background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));"></div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>Reclaimed Memory</h3>
                    <span style="color: var(--accent-emerald); font-family: var(--font-mono); font-size: 12px; font-weight: 700;">SESSION</span>
                </div>
                <div class="stat-value" id="stat-reclaimed" style="color: var(--accent-emerald);">0 MB</div>
                <div class="stat-sub">Total Working Set Memory Saved From SSD Paging</div>
                <div class="progress-bar-bg" style="background: rgba(16, 185, 129, 0.1);">
                    <div class="progress-bar-fill" style="width: 100%; background: var(--accent-emerald);"></div>
                </div>
            </div>
        </div>

        <!-- Quick Actions & Guardian Switch -->
        <div class="actions-panel">
            <div class="card">
                <div class="card-header">
                    <h3>Quick Flow Accelerators</h3>
                </div>
                <div class="btn-group">
                    <button class="btn-primary" onclick="triggerBoost()">
                        <span>⚡</span> Instant Turbo Boost
                    </button>
                    <button class="btn-secondary" onclick="triggerCleanTemp()">
                        <span>🧹</span> Purge Temp Cache
                    </button>
                    <button class="btn-danger" onclick="triggerKillZombies()">
                        <span>💀</span> Clear Stuck Workers
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>Autonomous Guardian</h3>
                </div>
                <div class="toggle-container">
                    <div>
                        <div style="font-weight: 700; font-size: 14px;">Auto-Trim RAM</div>
                        <div style="font-size: 12px; color: var(--text-muted);">Compacts idle RAM if > 82%</div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="daemon-toggle" checked onchange="toggleDaemon(this.checked)">
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
        </div>

        <!-- Process Breakdown & Live Logs -->
        <div class="data-section">
            <div class="card">
                <div class="card-header">
                    <h3>Top Memory Consumers</h3>
                    <span style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono);">Auto-updating</span>
                </div>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>PID</th>
                                <th>Process Name</th>
                                <th>Type</th>
                                <th style="text-align: right;">RAM (MB)</th>
                            </tr>
                        </thead>
                        <tbody id="process-table-body">
                            <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">Loading processes...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3>OptiFlow Event Log</h3>
                    <span style="font-size: 12px; color: var(--accent-cyan); font-family: var(--font-mono);">Live Feed</span>
                </div>
                <div class="log-box" id="log-box">
                    <div class="log-entry log-cyan">[System] OptiFlow performance console initialized.</div>
                </div>
            </div>
        </div>
    </div>

    <div id="toast">Action completed!</div>

    <script>
        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3500);
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                
                // Memory update
                const mem = data.memory;
                document.getElementById('stat-ram-used').textContent = mem.used_gb + ' GB';
                document.getElementById('stat-ram-total').textContent = mem.total_gb;
                document.getElementById('stat-ram-avail').textContent = mem.avail_gb;
                document.getElementById('ram-badge').textContent = mem.percent_used + '%';
                
                const ramBar = document.getElementById('ram-bar');
                ramBar.style.width = mem.percent_used + '%';
                if (mem.percent_used > 85) {
                    ramBar.style.background = 'linear-gradient(90deg, #f59e0b, #f43f5e)';
                } else {
                    ramBar.style.background = 'linear-gradient(90deg, #06b6d4, #8b5cf6)';
                }

                // Daemon status
                const d = data.daemon;
                document.getElementById('stat-reclaimed').textContent = d.total_ram_reclaimed_mb + ' MB';
                document.getElementById('daemon-toggle').checked = d.is_running;
                const guardianText = document.getElementById('header-guardian-text');
                if (d.is_running) {
                    guardianText.textContent = 'GUARDIAN ACTIVE';
                    guardianText.parentElement.style.color = 'var(--accent-emerald)';
                } else {
                    guardianText.textContent = 'GUARDIAN PAUSED';
                    guardianText.parentElement.style.color = 'var(--text-muted)';
                }

                // Process table
                const tbody = document.getElementById('process-table-body');
                tbody.innerHTML = '';
                data.top_processes.slice(0, 10).forEach(p => {
                    const tr = document.createElement('tr');
                    const badgeHtml = p.is_dev 
                        ? '<span class="badge-dev">DEV / CODE</span>'
                        : '<span class="badge-normal">APP</span>';
                    tr.innerHTML = `
                        <td style="font-family: var(--font-mono); color: var(--text-muted);">${p.pid}</td>
                        <td style="font-weight: 600;">${p.name}</td>
                        <td>${badgeHtml}</td>
                        <td style="text-align: right; font-family: var(--font-mono); font-weight: 700; color: ${p.memory_mb > 250 ? '#f43f5e' : '#f1f5f9'};">${p.memory_mb} MB</td>
                    `;
                    tbody.appendChild(tr);
                });

                // Logs update
                if (d.recent_logs && d.recent_logs.length > 0) {
                    const logBox = document.getElementById('log-box');
                    logBox.innerHTML = d.recent_logs.map(log => {
                        let colorClass = 'log-cyan';
                        if (log.includes('Recovered') || log.includes('started')) colorClass = 'log-green';
                        if (log.includes('high') || log.includes('error')) colorClass = 'log-amber';
                        return `<div class="log-entry ${colorClass}">${log}</div>`;
                    }).join('');
                    logBox.scrollTop = logBox.scrollHeight;
                }

            } catch (err) {
                console.error('Error fetching OptiFlow status:', err);
            }
        }

        async function triggerBoost() {
            try {
                showToast('⚡ Turbo Boosting: Compacting RAM & elevating P-Cores...');
                const res = await fetch('/api/boost', { method: 'POST' });
                const data = await res.json();
                showToast(`✅ Boost complete! Freed ${data.memory_trimmed.recovered_mb} MB RAM. Prioritized ${data.dev_boost.boosted_count} dev tasks.`);
                fetchStatus();
            } catch (err) {
                showToast('❌ Boost failed: ' + err);
            }
        }

        async function triggerCleanTemp() {
            try {
                showToast('🧹 Purging temporary caches and junk...');
                const res = await fetch('/api/clean_temp', { method: 'POST' });
                const data = await res.json();
                showToast(`✅ Cleaned ${data.cleaned_mb} MB of temp files (${data.deleted_files} files removed).`);
                fetchStatus();
            } catch (err) {
                showToast('❌ Temp clean failed: ' + err);
            }
        }

        async function triggerKillZombies() {
            try {
                showToast('💀 Scanning for stuck zombie processes...');
                const res = await fetch('/api/kill_zombies', { method: 'POST' });
                const data = await res.json();
                if (data.reaped_count > 0) {
                    showToast(`✅ Terminated ${data.reaped_count} stuck processes.`);
                } else {
                    showToast(`✅ No stuck compiler/worker zombies found.`);
                }
                fetchStatus();
            } catch (err) {
                showToast('❌ Zombie reaper failed: ' + err);
            }
        }

        async function toggleDaemon(enabled) {
            try {
                await fetch('/api/toggle_daemon', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enable: enabled })
                });
                showToast(enabled ? '🛡️ Guardian Daemon activated' : '⏸️ Guardian Daemon paused');
                fetchStatus();
            } catch (err) {
                showToast('❌ Failed to toggle guardian: ' + err);
            }
        }

        // Poll every 3 seconds
        setInterval(fetchStatus, 3000);
        fetchStatus();
    </script>
</body>
</html>
"""


class OptiFlowHandler(BaseHTTPRequestHandler):
    def _set_json_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
        elif parsed.path == '/api/status':
            mem = get_memory_status()
            processes = get_process_list()[:15]
            daemon_status = daemon_instance.get_status()
            
            data = {
                "memory": mem,
                "daemon": daemon_status,
                "top_processes": processes
            }
            self._set_json_headers(200)
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/boost':
            opt_mem = optimize_idle_memory(skip_foreground=True)
            boost_procs = boost_dev_flow()
            daemon_instance.total_ram_reclaimed_mb += opt_mem["recovered_mb"]
            daemon_instance.log(f"Manual Turbo Boost: Freed {opt_mem['recovered_mb']} MB RAM. Prioritized {boost_procs['boosted_count']} tasks.")
            
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "memory_trimmed": opt_mem,
                "dev_boost": boost_procs
            }).encode('utf-8'))

        elif parsed.path == '/api/clean_temp':
            res = clean_temp_cache()
            daemon_instance.log(f"Cleaned {res['cleaned_mb']} MB of temporary files.")
            self._set_json_headers(200)
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif parsed.path == '/api/kill_zombies':
            res = reap_zombies()
            if res["reaped_count"] > 0:
                daemon_instance.log(f"Terminated {res['reaped_count']} stuck zombie tasks.")
            self._set_json_headers(200)
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif parsed.path == '/api/toggle_daemon':
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'
            try:
                body = json.loads(post_body.decode('utf-8'))
                enable = body.get('enable', True)
            except Exception:
                enable = True

            if enable and not daemon_instance.is_running:
                daemon_instance.start()
            elif not enable and daemon_instance.is_running:
                daemon_instance.stop()

            self._set_json_headers(200)
            self.wfile.write(json.dumps({"is_running": daemon_instance.is_running}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging to console
        pass


def run_server(port=5050):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, OptiFlowHandler)
    print(f"\n=======================================================")
    print(f">> OptiFlow Server running at: http://localhost:{port}")
    print(f">> Background Guardian Daemon is active.")
    print(f"=======================================================\n")
    
    # Start guardian daemon automatically
    daemon_instance.start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down OptiFlow Server...")
        daemon_instance.stop()
        httpd.server_close()


if __name__ == '__main__':
    port = 5050
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
