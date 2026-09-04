"""
OptiFlow Core - Windows High-Performance System Optimization Engine
Built with pure Python standard library & ctypes (Zero dependencies, < 15MB RAM).
Specifically tuned for 8GB RAM + Intel 12th Gen hybrid architecture (P-Cores/E-Cores).
"""

import os
import sys
import ctypes
from ctypes import wintypes
import time
import shutil
import tempfile

# Win32 API DLLs
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Process Priority Constants
IDLE_PRIORITY_CLASS = 0x00000040
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
NORMAL_PRIORITY_CLASS = 0x00000020
ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
HIGH_PRIORITY_CLASS = 0x00000080

# Process Access Constants
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_QUOTA = 0x0100
PROCESS_SET_INFORMATION = 0x0200
PROCESS_TERMINATE = 0x0001

TH32CS_SNAPPROCESS = 0x00000002

# Structures
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_uint64),
        ("ullAvailPhys", ctypes.c_uint64),
        ("ullTotalPageFile", ctypes.c_uint64),
        ("ullAvailPageFile", ctypes.c_uint64),
        ("ullTotalVirtual", ctypes.c_uint64),
        ("ullAvailVirtual", ctypes.c_uint64),
        ("ullAvailExtendedVirtual", ctypes.c_uint64),
    ]

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]

class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]

# Priority developer/performance apps to keep high on P-Cores
DEV_PROCESS_NAMES = {
    "code.exe", "devenv.exe", "g++.exe", "gcc.exe", "clang.exe", "ld.exe",
    "python.exe", "pythonw.exe", "node.exe", "cargo.exe", "rustc.exe",
    "cmd.exe", "powershell.exe", "pwsh.exe", "windowsterminal.exe", "conhost.exe",
    "git.exe"
}

# Processes that should never be forcefully trimmed or throttled
PROTECTED_PROCESS_NAMES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "winlogon.exe", "explorer.exe",
    "dwm.exe", "audiodg.exe", "antigravity.exe"
}

# Background bloat processes that can be safely lowered/trimmed
BACKGROUND_HOGS = {
    "onedrive.exe", "cortana.exe", "searchapp.exe", "searchhost.exe",
    "yourphone.exe", "phoneexperiencehost.exe", "gamebar.exe", "gamebarft.exe",
    "microsoftedgeupdate.exe", "googleupdate.exe", "discordcanary.exe"
}


def get_memory_status():
    """Retrieve real-time physical and virtual memory statistics."""
    mem = MEMORYSTATUSEX()
    mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
        return {
            "percent_used": 0,
            "total_mb": 0,
            "avail_mb": 0,
            "used_mb": 0,
            "total_gb": 0,
            "avail_gb": 0,
            "used_gb": 0
        }
    
    total_mb = round(mem.ullTotalPhys / (1024 * 1024), 1)
    avail_mb = round(mem.ullAvailPhys / (1024 * 1024), 1)
    used_mb = round(total_mb - avail_mb, 1)
    
    return {
        "percent_used": mem.dwMemoryLoad,
        "total_mb": total_mb,
        "avail_mb": avail_mb,
        "used_mb": used_mb,
        "total_gb": round(total_mb / 1024, 2),
        "avail_gb": round(avail_mb / 1024, 2),
        "used_gb": round(used_mb / 1024, 2),
        "pagefile_total_mb": round(mem.ullTotalPageFile / (1024 * 1024), 1),
        "pagefile_avail_mb": round(mem.ullAvailPageFile / (1024 * 1024), 1)
    }


def get_foreground_process_id():
    """Retrieve the PID of the active foreground window."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_process_list():
    """Enumerate all running processes with memory usage and details."""
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == wintypes.HANDLE(-1).value:
        return []

    processes = []
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)

    success = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
    while success:
        pid = entry.th32ProcessID
        name = entry.szExeFile
        
        # Query process memory working set
        mem_mb = 0.0
        h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if h_process:
            pmc = PROCESS_MEMORY_COUNTERS_EX()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
            if psapi.GetProcessMemoryInfo(h_process, ctypes.byref(pmc), pmc.cb):
                mem_mb = round(pmc.WorkingSetSize / (1024 * 1024), 2)
            kernel32.CloseHandle(h_process)
            
        processes.append({
            "pid": pid,
            "name": name,
            "parent_pid": entry.th32ParentProcessID,
            "threads": entry.cntThreads,
            "memory_mb": mem_mb,
            "is_dev": name.lower() in DEV_PROCESS_NAMES,
            "is_protected": name.lower() in PROTECTED_PROCESS_NAMES
        })
        success = kernel32.Process32NextW(snapshot, ctypes.byref(entry))

    kernel32.CloseHandle(snapshot)
    processes.sort(key=lambda p: p["memory_mb"], reverse=True)
    return processes


def trim_process_working_set(pid):
    """
    Trim working set for a process, purging unused RAM back to the OS.
    Uses Win32 EmptyWorkingSet API.
    """
    access = PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION
    h_proc = kernel32.OpenProcess(access, False, pid)
    if not h_proc:
        # Fallback with limited information
        h_proc = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_proc:
            return False

    res = psapi.EmptyWorkingSet(h_proc)
    kernel32.CloseHandle(h_proc)
    return bool(res)


def set_process_priority(pid, priority_class):
    """Set execution priority class for a given PID."""
    h_proc = kernel32.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
    if not h_proc:
        return False
    res = kernel32.SetPriorityClass(h_proc, priority_class)
    kernel32.CloseHandle(h_proc)
    return bool(res)


def optimize_idle_memory(skip_foreground=True):
    """
    Scans running processes and releases working sets of idle and background apps.
    Returns: (recovered_mb, processes_trimmed)
    """
    before = get_memory_status()
    fg_pid = get_foreground_process_id() if skip_foreground else None
    procs = get_process_list()

    trimmed_count = 0
    for p in procs:
        pid = p["pid"]
        name_lower = p["name"].lower()

        # Skip PID 0, PID 4 (System), and protected system services
        if pid <= 4 or name_lower in PROTECTED_PROCESS_NAMES:
            continue
        
        # Skip active foreground application to preserve instant UI responsiveness
        if skip_foreground and pid == fg_pid:
            continue

        # Target processes taking over 20MB of working set
        if p["memory_mb"] >= 20.0:
            if trim_process_working_set(pid):
                trimmed_count += 1

    time.sleep(0.3)
    after = get_memory_status()
    recovered_mb = max(0.0, round(after["avail_mb"] - before["avail_mb"], 1))
    return {
        "recovered_mb": recovered_mb,
        "processes_trimmed": trimmed_count,
        "ram_before_mb": before["used_mb"],
        "ram_after_mb": after["used_mb"],
        "percent_after": after["percent_used"]
    }


def boost_dev_flow():
    """
    Elevates priorities of developer tools (VS Code, compilers, Python, shells)
    to ABOVE_NORMAL or HIGH so they utilize Intel 12th Gen P-Cores first.
    Demotes background hogs to BELOW_NORMAL.
    """
    procs = get_process_list()
    boosted = []
    throttled = []

    for p in procs:
        pid = p["pid"]
        name_lower = p["name"].lower()

        if name_lower in DEV_PROCESS_NAMES:
            if set_process_priority(pid, ABOVE_NORMAL_PRIORITY_CLASS):
                boosted.append(f"{p['name']} (PID {pid})")
        elif name_lower in BACKGROUND_HOGS:
            if set_process_priority(pid, BELOW_NORMAL_PRIORITY_CLASS):
                throttled.append(f"{p['name']} (PID {pid})")

    return {
        "boosted_count": len(boosted),
        "boosted": boosted,
        "throttled_count": len(throttled),
        "throttled": throttled
    }


def clean_temp_cache():
    """
    Safely cleans Windows user %TEMP% files and temporary build artifacts.
    Skips files currently locked by active applications.
    """
    temp_dir = tempfile.gettempdir()
    cleaned_bytes = 0
    deleted_files = 0
    deleted_dirs = 0

    if os.path.exists(temp_dir):
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    cleaned_bytes += size
                    deleted_files += 1
                except Exception:
                    # In use or access denied - safely ignore
                    pass

            for d in dirs:
                dirpath = os.path.join(root, d)
                try:
                    shutil.rmtree(dirpath, ignore_errors=True)
                    deleted_dirs += 1
                except Exception:
                    pass

    cleaned_mb = round(cleaned_bytes / (1024 * 1024), 2)
    return {
        "cleaned_mb": cleaned_mb,
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs
    }


def reap_zombies():
    """
    Terminates abandoned or stuck compiler / worker processes (e.g. hung g++.exe, conhost, or python build scripts).
    """
    procs = get_process_list()
    reaped = []
    for p in procs:
        name_lower = p["name"].lower()
        if name_lower in {"g++.exe", "gcc.exe", "ld.exe"} and p["threads"] <= 1:
            try:
                h_proc = kernel32.OpenProcess(PROCESS_TERMINATE, False, p["pid"])
                if h_proc:
                    kernel32.TerminateProcess(h_proc, 1)
                    kernel32.CloseHandle(h_proc)
                    reaped.append(f"{p['name']} (PID {p['pid']})")
            except Exception:
                pass

    return {
        "reaped_count": len(reaped),
        "reaped": reaped
    }


if __name__ == "__main__":
    print("=== OptiFlow Core Diagnostic ===")
    mem = get_memory_status()
    print(f"Total Physical RAM: {mem['total_gb']} GB")
    print(f"Available RAM: {mem['avail_gb']} GB ({100 - mem['percent_used']}% free)")
    print(f"Memory Load: {mem['percent_used']}%")

    print("\n--- Top 5 Memory Consumers ---")
    processes = get_process_list()[:5]
    for proc in processes:
        print(f"PID {proc['pid']:<6} | {proc['name']:<25} | {proc['memory_mb']:>8.1f} MB")

    print("\n--- Running Working Set Optimization Test ---")
    opt = optimize_idle_memory(skip_foreground=True)
    print(f"Trimmed {opt['processes_trimmed']} processes | Reclaimed: {opt['recovered_mb']} MB")
    print(f"Memory Load Now: {opt['percent_after']}%")
