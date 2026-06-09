"""Runtime discovery helpers."""

from __future__ import annotations

import socket
from pathlib import Path

from mxm.types import MachineId, RuntimeSubstrate

DEFAULT_DOCKERENV_PATH = Path("/.dockerenv")


def discover_machine() -> MachineId:
    """Discover the current MXM machine identifier.

    The machine identifier is the canonical MXM name of the physical host.

    For v0.1, MXM assumes that managed hosts use stable hostnames which
    correspond directly to the machine identifier.

    Examples
    --------
    bridge
    wildling
    monolith
    """
    return MachineId(socket.gethostname())


def discover_substrate(
    *,
    dockerenv_path: Path = DEFAULT_DOCKERENV_PATH,
) -> RuntimeSubstrate:
    """Discover the current execution substrate.

    Discovery order:

    1. Docker marker file.
    2. ``local-process`` fallback.

    The Docker marker path is injectable because ``/.dockerenv`` is a
    conventional probe rather than an MXM-owned runtime concept.
    """
    if dockerenv_path.exists():
        return RuntimeSubstrate("docker-container")

    return RuntimeSubstrate("local-process")
