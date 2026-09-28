from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mxm.config import MXMConfig
from mxm.types import RuntimeIdentity


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    """Resolved filesystem locations available to this runtime."""

    data_root: Path
    artifact_root: Path
    export_root: Path
    log_root: Path


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    """Resolved context for MXM application composition."""

    identity: RuntimeIdentity
    config: MXMConfig
    paths: RuntimePaths
