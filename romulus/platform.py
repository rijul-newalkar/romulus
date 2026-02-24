import platform
from pathlib import Path

from pydantic import BaseModel


class PlatformInfo(BaseModel):
    system: str
    is_pi: bool
    is_mac: bool
    hostname: str
    python_version: str
    machine: str


def detect_platform() -> PlatformInfo:
    system = platform.system()
    machine = platform.machine()
    is_pi = (
        system == "Linux"
        and machine in ("aarch64", "armv7l")
        and Path("/proc/device-tree/model").exists()
    )
    is_mac = system == "Darwin"

    return PlatformInfo(
        system=system,
        is_pi=is_pi,
        is_mac=is_mac,
        hostname=platform.node(),
        python_version=platform.python_version(),
        machine=machine,
    )
