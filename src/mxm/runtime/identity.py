"""Runtime identity construction.

This module provides the small public construction helper for MXM runtime
identity. It deliberately keeps discovery and validation at the boundary:
callers may pass explicit values, while missing machine/substrate values are
delegated to discovery helpers.
"""

from __future__ import annotations

from mxm.runtime.discovery import discover_machine, discover_substrate
from mxm.runtime.validation import validate_runtime_identity_shape
from mxm.types import (
    RuntimeIdentity,
)


def build_runtime_identity(
    *,
    app: str,
    environment: str,
    role: str,
    machine: str | None = None,
    substrate: str | None = None,
) -> RuntimeIdentity:
    """Build and validate a RuntimeIdentity.

    Parameters
    ----------
    app:
        MXM application identifier used to select application configuration.
    environment:
        Operational environment, for example ``dev``, ``test``, or ``prod``.
    role:
        Runtime responsibility and configuration selector, for example
        ``research`` or ``marketdata``. This is not an authentication or
        authorization role.
    machine:
        Machine-specific runtime configuration selector. If omitted, this is
        discovered from the local host.
    substrate:
        Execution substrate. If omitted, this is discovered.

    Returns
    -------
    RuntimeIdentity
        A validated runtime identity using the shared mxm-types vocabulary.
    """
    resolved_machine = machine if machine is not None else discover_machine()
    resolved_substrate = substrate if substrate is not None else discover_substrate()

    identity = RuntimeIdentity(
        app=app,
        environment=environment,
        machine=resolved_machine,
        substrate=resolved_substrate,
        role=role,
    )

    validate_runtime_identity_shape(identity)

    return identity
