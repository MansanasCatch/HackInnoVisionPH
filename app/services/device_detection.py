"""Hardware detection utility using psutil and platform inspection."""

import os
import platform
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

    # OS name
    os_name = f"{platform.system()} {platform.release()}".strip()

    # GPU & VRAM detection
    gpu_name, vram_gb = _detect_gpu_info()

    return DeviceSpecsDetect(
        ram_gb=ram_gb,
        gpu_name=gpu_name,
        vram_gb=vram_gb,
        cpu_cores=cpu_cores,
        storage_free_gb=storage_free_gb,
        os_name=os_name,
    )


def _detect_gpu_info() -> tuple[str | None, float]:
    """Attempt to detect discrete GPU name and dedicated VRAM in GB."""
    # 1. Try PyTorch CUDA if installed
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = round(vram_bytes / (1024**3), 1)
            return name, vram_gb
    except Exception:
        pass

    # 2. Try nvidia-smi command line
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

    # 3. Try Windows WMIC / PowerShell query for display adapters
    if os.name == "nt":
        try:
            cmd = (
                'powershell -Command "Get-CimInstance Win32_VideoController '
                '| Select-Name Name,AdapterRAM | ConvertTo-Json"'
            )
            res = subprocess.check_output(cmd, shell=True, text=True, timeout=3.0).strip()
            if "NVIDIA" in res or "AMD" in res or "Radeon" in res or "Intel" in res:
                # Basic check for GPU name
                for line in res.splitlines():
                    if '"Name"' in line and ":" in line:
                        name = line.split(":", 1)[1].replace('"', "").replace(",", "").strip()
                        return name, 0.0
        except Exception:
            pass

    return "Integrated Graphics / Standard Display", 0.0
