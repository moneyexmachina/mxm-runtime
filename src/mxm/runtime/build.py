"""RuntimeContext construction for mxm-runtime.

This module owns materialisation of a RuntimeContext from an explicit
RuntimeIdentity and resolved MXM configuration.

It deliberately keeps package responsibilities separated:

- mxm-config loads, slices, and converts configuration.
- mxm-secrets constructs the configured SecretsApi from plain config data.
- mxm-runtime assembles the materialised RuntimeContext.
"""

from __future__ import annotations

from pathlib import Path

from mxm.config import load_config, make_view, to_config_data
from mxm.runtime.context import RuntimeContext
from mxm.secrets import SecretsApi
from mxm.types import RuntimeIdentity


def build_runtime_context(
    *,
    identity: RuntimeIdentity,
    store_root: Path | None = None,
) -> RuntimeContext:
    """Build a RuntimeContext for an explicit runtime identity.

    Parameters
    ----------
    identity
        Runtime identity used to resolve configuration and materialise runtime
        services.
    store_root
        Optional configuration store root. If omitted, mxm-config uses its
        default configuration store location.

    Returns
    -------
    RuntimeContext
        Materialised runtime context containing the supplied identity, resolved
        configuration, and configured SecretsApi.

    Raises
    ------
    FileNotFoundError
        If required configuration files are missing.
    KeyError
        If selected configuration layers or required config sections are absent.
    TypeError
        If configuration sections have invalid structure.
    ValueError
        If secrets configuration fails mxm-secrets validation.
    """
    if store_root is None:
        config = load_config(identity=identity)
    else:
        config = load_config(
            identity=identity,
            store_root=store_root,
        )

    secrets_config = make_view(
        config,
        "mxm_secrets",
        readonly=True,
        resolve=True,
    )

    secrets = SecretsApi.from_config_data(
        to_config_data(secrets_config),
    )

    return RuntimeContext(
        identity=identity,
        config=config,
        secrets=secrets,
    )
