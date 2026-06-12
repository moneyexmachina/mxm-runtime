"""Runtime discovery helpers."""

from __future__ import annotations

import socket
from pathlib import Path

DEFAULT_DOCKERENV_PATH = Path("/.dockerenv")


def discover_machine() -> str:
    """Discover the current MXM machine selector.

    The machine selector identifies the machine-specific configuration profile
    that should be applied by MXM.

    It is derived from operating-system host information but is not required to
    equal the raw hostname reported by the operating system. The purpose of the
    selector is configuration selection rather than unique host identification.

    For v0.1, the selector is derived from the local hostname by taking the
    unqualified hostname component.

    Examples
    --------
    Raw hostname:

        bridge.local

    Produces:

        bridge

    Raw hostname:

        monolith

    Produces:

        monolith

    Returns
    -------
    str
        MXM machine selector used for machine-specific configuration loading.
    """
    hostname = socket.gethostname()
    return hostname.split(".", maxsplit=1)[0]


def discover_substrate(
    *,
    dockerenv_path: Path = DEFAULT_DOCKERENV_PATH,
) -> str:
    """Discover the current execution substrate.

    Discovery order:

    1. Docker marker file.
    2. ``local-process`` fallback.

    The Docker marker path is injectable because ``/.dockerenv`` is a
    conventional probe rather than an MXM-owned runtime concept.
    """
    if dockerenv_path.exists():
        return "docker-container"

    return "local-process"
