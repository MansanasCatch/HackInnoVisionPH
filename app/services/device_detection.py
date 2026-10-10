"""Hardware detection utility supporting Windows, macOS (Apple Silicon & Intel), and Linux."""

import os
import platform
import re
import subprocess

import psutil

from app.schemas.device import DeviceSpecsDetect


def detect_system_hardware() -> DeviceSpecsDetect:
    """Detect RAM, CPU, GPU/VRAM, free storage, and OS name of the host machine."""
    # RAM in GB
    total_ram_bytes = psutil.virtual_memory().total
    ram_gb = round(total_ram_bytes / (1024**3), 1)

    # CPU cores
    cpu_cores = psutil.cpu_count(logical=True) or 4

    # Free storage in GB
    try:
        root_path = "C:\\" if os.name == "nt" else "/"
        storage_free_bytes = psutil.disk_usage(root_path).free
        storage_free_gb = round(storage_free_bytes / (1024**3), 1)
    except Exception:
        storage_free_gb = 50.0

    # User-friendly OS name across Windows, macOS, and Linux
    os_name = _detect_os_name()

    # GPU & VRAM detection (Windows, macOS Apple Silicon/Intel/AMD, Linux)
    gpu_name, vram_gb = _detect_gpu_info(ram_gb=ram_gb)

    return DeviceSpecsDetect(
        ram_gb=ram_gb,
        gpu_name=gpu_name,
        vram_gb=vram_gb,
        cpu_cores=cpu_cores,
        storage_free_gb=storage_free_gb,
        os_name=os_name,
    )


def _detect_os_name() -> str:
    """Return user-friendly OS identification for Windows, macOS, and Linux."""
    system = platform.system()
    if system == "Darwin":
        mac_ver = platform.mac_ver()[0]
        codename = ""
        if mac_ver:
            major = mac_ver.split(".")[0]
            codenames = {
                "15": "Sequoia",
                "14": "Sonoma",
                "13": "Ventura",
                "12": "Monterey",
                "11": "Big Sur",
                "10": "Catalina",
            }
            if major in codenames:
                codename = f" ({codenames[major]})"
        return f"macOS {mac_ver}{codename}".strip() if mac_ver else "macOS"

    if system == "Windows":
        release = platform.release()
        return f"Windows {release}".strip()

    return f"{system} {platform.release()}".strip()


def _detect_gpu_info(ram_gb: float = 8.0) -> tuple[str | None, float]:
    """Attempt to detect discrete GPU name and dedicated VRAM across macOS, Windows, and Linux."""
    system = platform.system()

    # 1. macOS (Apple Silicon M1/M2/M3/M4 or Intel/AMD graphics)
    if system == "Darwin":
        return _detect_macos_gpu(ram_gb=ram_gb)

    # 2. Windows & Linux: Try PyTorch CUDA if installed
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = round(vram_bytes / (1024**3), 1)
            return name, vram_gb
    except Exception:
        pass

    # 3. Windows & Linux: Try nvidia-smi command line
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            text=True,
            timeout=2.0,
        ).strip()
        if output:
            parts = output.split(",")
            gpu_name = parts[0].strip()
            vram_mb = float(parts[1].strip())
            return gpu_name, round(vram_mb / 1024.0, 1)
    except Exception:
        pass

    # 4. Windows: Try Windows registry for instant zero-overhead GPU lookup
    if system == "Windows" or os.name == "nt":
        return _detect_windows_gpu()

    return "Integrated Graphics / Standard Display", 0.0


def _detect_macos_gpu(ram_gb: float) -> tuple[str | None, float]:
    """Detect Apple Silicon (M1/M2/M3/M4) or Intel/AMD graphics on macOS."""
    # Check for Apple Silicon chip via sysctl machdep.cpu.brand_string
    try:
        brand = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            text=True,
            timeout=1.0,
        ).strip()
        if "Apple" in brand:
            # Apple Silicon uses Unified Memory architecture; Metal GPU can access up to ~75% of RAM
            effective_vram = round(ram_gb * 0.75, 1)
            return f"{brand} (Metal GPU)", effective_vram
    except Exception:
        pass

    # Fallback for macOS: system_profiler SPDisplaysDataType
    try:
        output = subprocess.check_output(
            ["system_profiler", "SPDisplaysDataType"],
            text=True,
            timeout=2.5,
        )
        chipset = None
        vram = 0.0
        for line in output.splitlines():
            line_strip = line.strip()
            if line_strip.startswith("Chipset Model:"):
                chipset = line_strip.split("Chipset Model:", 1)[1].strip()
            elif "VRAM" in line_strip:
                match_gb = re.search(r"(\d+(?:\.\d+)?)\s*GB", line_strip, re.IGNORECASE)
                match_mb = re.search(r"(\d+(?:\.\d+)?)\s*MB", line_strip, re.IGNORECASE)
                if match_gb:
                    vram = float(match_gb.group(1))
                elif match_mb:
                    vram = round(float(match_mb.group(1)) / 1024.0, 1)

        if chipset:
            if "Apple" in chipset:
                vram = max(vram, round(ram_gb * 0.75, 1))
                return f"{chipset} (Metal GPU)", vram
            return chipset, vram
    except Exception:
        pass

    # Check architecture
    if platform.machine() == "arm64":
        return "Apple Silicon (Metal GPU)", round(ram_gb * 0.75, 1)

    return "Intel Iris / Mac Display", 0.0


def _detect_windows_gpu() -> tuple[str | None, float]:
    """Inspect Windows registry and PowerShell for graphics adapters and dedicated VRAM."""
    try:
        import winreg

        video_class_path = (
            r"SYSTEM\CurrentControlSet\Control\Class"
            r"\{4d36e968-e325-11ce-bfc1-08002be10318}"
        )
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, video_class_path) as class_key:
            for subkey_name in ("0000", "0001", "0002"):
                try:
                    with winreg.OpenKey(class_key, subkey_name) as dev_key:
                        desc, _ = winreg.QueryValueEx(dev_key, "DriverDesc")
                        if desc and isinstance(desc, str):
                            vram_gb = 0.0
                            # Check for dedicated memory size in registry
                            for val_name in ("HardwareInformation.qwMemorySize", "HardwareInformation.MemorySize"):
                                try:
                                    mem_val, _ = winreg.QueryValueEx(dev_key, val_name)
                                    if mem_val and isinstance(mem_val, int) and mem_val > 0:
                                        vram_gb = round(mem_val / (1024**3), 1)
                                        break
                                except OSError:
                                    pass
                            return desc.strip(), vram_gb
                except OSError:
                    continue
    except Exception:
        pass

    # Fallback to PowerShell
    try:
        cmd = (
            'powershell -NoProfile -Command "Get-CimInstance Win32_VideoController '
            '| Select-Object -Property Name, AdapterRAM"'
        )
        res = subprocess.check_output(cmd, shell=True, text=True, timeout=1.5).strip()
        lines = [
            line.strip()
            for line in res.splitlines()
            if line.strip() and not line.strip().startswith("Name") and not line.strip().startswith("----")
        ]
        if lines:
            parts = lines[0].split()
            name = " ".join(parts[:-1]) if len(parts) > 1 and parts[-1].isdigit() else lines[0]
            vram = 0.0
            if len(parts) > 1 and parts[-1].isdigit():
                vram = round(int(parts[-1]) / (1024**3), 1)
            return name, vram
    except Exception:
        pass

    return "Integrated Graphics / Standard Display", 0.0
