from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mxm.config import MXMConfig
from mxm.secrets import SecretsApi
from mxm.types import RuntimeIdentity


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    """Resolved filesystem locations available to this runtime."""

    data_root: Path
    artifact_root: Path
    export_root: Path
    log_root: Path


@dataclass(frozen=True, slots=True)
class RuntimeMetadata:
    """Materialised metadata about the current execution substrate."""

    substrate: str
    is_container: bool


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    """Materialised operational context for an MXM runtime."""

    identity: RuntimeIdentity
    config: MXMConfig
    secrets: SecretsApi | None = None
    db_configs: MXMConfig | None = None
    paths: RuntimePaths | None = None
    runtime: RuntimeMetadata | None = None
