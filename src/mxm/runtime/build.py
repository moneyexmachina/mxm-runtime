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

from mxm.config import MXMConfig, load_config, make_view, to_config_data
from mxm.runtime.context import RuntimeContext, RuntimePaths
from mxm.secrets import SecretsApi
from mxm.types import JSONMap, RuntimeIdentity


def _required_string(data: JSONMap, key: str) -> str:
    """Return a required string value from plain config data."""
    value = data[key]

    if not isinstance(value, str):
        raise TypeError(f"Expected '{key}' to be a string, got {type(value).__name__}.")

    return value


def _build_runtime_paths(config: MXMConfig) -> RuntimePaths:
    """Materialise resolved runtime filesystem paths from configuration."""
    paths_config = make_view(
        config,
        "mxm_paths",
        readonly=True,
        resolve=True,
    )
    paths_data = to_config_data(paths_config)

    return RuntimePaths(
        data_root=Path(_required_string(paths_data, "data_root")).expanduser(),
        artifact_root=Path(_required_string(paths_data, "artifact_root")).expanduser(),
        export_root=Path(_required_string(paths_data, "export_root")).expanduser(),
        log_root=Path(_required_string(paths_data, "log_root")).expanduser(),
    )


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
    db_configs = make_view(
        config,
        "mxm_databases",
        readonly=True,
        resolve=True,
    )

    paths = _build_runtime_paths(config)
    return RuntimeContext(
        identity=identity,
        config=config,
        secrets=secrets,
        db_configs=db_configs,
        paths=paths,
    )
