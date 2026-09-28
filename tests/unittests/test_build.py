"""Tests for RuntimeContext resolution."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

import mxm.runtime.build as runtime_build
from mxm.runtime.context import RuntimeContext
from mxm.types import RuntimeIdentity


def test_resolve_runtime_context_preserves_identity_selected_configuration(
    tmp_path: Path,
) -> None:
    """Identity-selected machine and environment layers should remain resolved."""
    store_root = _write_config_store(tmp_path)

    bridge_context = _resolve_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=store_root,
    )
    monolith_context = _resolve_runtime_context(
        identity=_identity(machine="monolith", environment="prod"),
        store_root=store_root,
    )

    assert bridge_context.config.mxm_machine.root == "~/.mxm"
    assert bridge_context.config.mxm_environment.name == "dev"
    assert monolith_context.config.mxm_machine.root == "/srv/mxm"
    assert monolith_context.config.mxm_environment.name == "prod"


def test_resolve_runtime_context_preserves_capability_namespaces(
    tmp_path: Path,
) -> None:
    """Capability-owned configuration should remain on the resolved config."""
    context = _resolve_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=_write_config_store(tmp_path),
    )

    assert context.config.mxm_secrets.refs.databento_api_key.store == "red"
    assert context.config.mxm_secrets.stores.black.backend == "gopass"
    assert context.config.mxm_databases.operational_state.driver == "postgresql"
    assert context.config.mxm_databases.operational_state.name == "mxm_dev"


def test_resolve_runtime_context_resolves_machine_and_environment_paths(
    tmp_path: Path,
) -> None:
    """Machine and environment config should jointly resolve runtime paths."""
    store_root = _write_config_store(tmp_path)

    bridge_context = _resolve_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=store_root,
    )
    monolith_context = _resolve_runtime_context(
        identity=_identity(machine="monolith", environment="prod"),
        store_root=store_root,
    )
    bridge_paths = bridge_context.paths
    monolith_paths = monolith_context.paths
    assert bridge_paths is not None
    assert monolith_paths is not None

    assert bridge_paths.data_root == Path("~/.mxm/dev/data").expanduser()
    assert bridge_paths.artifact_root == Path("~/.mxm/dev/artifacts").expanduser()
    assert bridge_paths.export_root == Path("~/.mxm/dev/exports").expanduser()
    assert bridge_paths.log_root == Path("~/.mxm/dev/logs").expanduser()

    assert monolith_paths.data_root == Path("/srv/mxm/prod/data")
    assert monolith_paths.artifact_root == Path("/srv/mxm/prod/artifacts")
    assert monolith_paths.export_root == Path("/srv/mxm/prod/exports")
    assert monolith_paths.log_root == Path("/srv/mxm/prod/logs")


def test_resolve_runtime_context_does_not_require_mxm_secrets(
    tmp_path: Path,
) -> None:
    """Runtime resolution should not require secrets capability configuration."""
    identity = _identity(machine="bridge", environment="dev")

    context = _resolve_runtime_context(
        identity=identity,
        store_root=_write_config_store_without_mxm_secrets(tmp_path),
    )
    paths = context.paths
    assert paths is not None

    assert context.identity == identity
    assert paths.data_root == Path("/tmp/mxm/data")


def test_resolve_runtime_context_does_not_require_mxm_databases(
    tmp_path: Path,
) -> None:
    """Runtime resolution should not require database capability configuration."""
    identity = _identity(machine="bridge", environment="dev")

    context = _resolve_runtime_context(
        identity=identity,
        store_root=_write_config_store_without_mxm_databases(tmp_path),
    )
    paths = context.paths
    assert paths is not None

    assert context.identity == identity
    assert paths.data_root == Path("/tmp/mxm/data")


def test_resolve_runtime_context_does_not_validate_mxm_secrets_schema(
    tmp_path: Path,
) -> None:
    """Secrets schema validation should remain with the capability owner."""
    context = _resolve_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=_write_config_store_with_invalid_store(tmp_path),
    )
    paths = context.paths
    assert paths is not None

    assert context.config.mxm_secrets.stores.red == "not-a-mapping"
    assert paths.data_root == Path("/tmp/mxm/data")


def test_resolve_runtime_context_rejects_missing_mxm_paths(
    tmp_path: Path,
) -> None:
    """Runtime resolution should continue to require runtime path configuration."""
    with pytest.raises(KeyError, match="mxm_paths"):
        _resolve_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=_write_config_store_without_mxm_paths(tmp_path),
        )


def test_resolve_runtime_context_rejects_invalid_path_config(
    tmp_path: Path,
) -> None:
    """Runtime resolution should continue to reject non-string path values."""
    with pytest.raises(TypeError, match="data_root"):
        _resolve_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=_write_config_store_with_invalid_paths(tmp_path),
        )


def _resolve_runtime_context(
    *,
    identity: RuntimeIdentity,
    store_root: Path,
) -> RuntimeContext:
    """Call the accepted resolver while keeping old implementations collectable."""
    resolver = getattr(runtime_build, "resolve_runtime_context", None)
    assert callable(resolver), "mxm.runtime.build must expose resolve_runtime_context"
    typed_resolver = cast(Callable[..., RuntimeContext], resolver)
    return typed_resolver(identity=identity, store_root=store_root)


def _identity(*, machine: str, environment: str) -> RuntimeIdentity:
    """Return a test runtime identity for config loading."""
    return RuntimeIdentity(
        app="mxm-runtime-test",
        environment=environment,
        machine=machine,
        substrate="local-process",
        role="marketdata",
    )


def _write_config_store(tmp_path: Path) -> Path:
    """Write a temporary mxm-config-store with runtime configuration."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)

    (app_root / "default.yaml").write_text(
        """\
mxm_secrets:
  refs:
    databento_api_key:
      store: red
      path: marketdata/databento/api_key
      policy: marketdata_access

  policies:
    marketdata_access:
      allowed_principals:
        - marketdata
        - research

mxm_databases:
  operational_state:
    driver: postgresql

mxm_paths:
  data_root: ${mxm_machine.root}/${mxm_environment.name}/data
  artifact_root: ${mxm_machine.root}/${mxm_environment.name}/artifacts
  export_root: ${mxm_machine.root}/${mxm_environment.name}/exports
  log_root: ${mxm_machine.root}/${mxm_environment.name}/logs
""",
        encoding="utf-8",
    )

    (app_root / "environment.yaml").write_text(
        """\
dev:
  mxm_environment:
    name: dev

  mxm_databases:
    operational_state:
      name: mxm_dev

prod:
  mxm_environment:
    name: prod

  mxm_databases:
    operational_state:
      name: mxm_prod
""",
        encoding="utf-8",
    )

    (app_root / "machine.yaml").write_text(
        """\
bridge:
  mxm_machine:
    root: ~/.mxm

  mxm_secrets:
    stores:
      red:
        backend: gopass
        root: mxm/red
      black:
        backend: gopass
        root: mxm/black

monolith:
  mxm_machine:
    root: /srv/mxm

  mxm_secrets:
    stores:
      red:
        backend: gopass
        root: mxm/red
""",
        encoding="utf-8",
    )

    return tmp_path


def _write_config_store_without_mxm_secrets(tmp_path: Path) -> Path:
    """Write a temporary config store missing the mxm_secrets section."""
    return _write_minimal_config_store(
        tmp_path,
        capability_config="""\
mxm_databases:
  operational_state:
    driver: postgresql
""",
    )


def _write_config_store_without_mxm_databases(tmp_path: Path) -> Path:
    """Write a temporary config store missing the mxm_databases section."""
    return _write_minimal_config_store(
        tmp_path,
        capability_config="""\
mxm_secrets:
  stores: {}
  refs: {}
  policies: {}
""",
    )


def _write_config_store_without_mxm_paths(tmp_path: Path) -> Path:
    """Write a temporary config store missing the mxm_paths section."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)
    (app_root / "default.yaml").write_text(
        """\
mxm_secrets:
  stores: {}
  refs: {}
  policies: {}

mxm_databases:
  operational_state:
    driver: postgresql
""",
        encoding="utf-8",
    )
    return tmp_path


def _write_config_store_with_invalid_store(tmp_path: Path) -> Path:
    """Write a config store with capability-invalid secrets configuration."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)
    (app_root / "default.yaml").write_text(
        """\
mxm_secrets:
  stores:
    red: not-a-mapping

mxm_paths:
  data_root: /tmp/mxm/data
  artifact_root: /tmp/mxm/artifacts
  export_root: /tmp/mxm/exports
  log_root: /tmp/mxm/logs
""",
        encoding="utf-8",
    )
    return tmp_path


def _write_config_store_with_invalid_paths(tmp_path: Path) -> Path:
    """Write a temporary config store with invalid path config."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)
    (app_root / "default.yaml").write_text(
        """\
mxm_secrets:
  stores: {}
  refs: {}
  policies: {}

mxm_databases:
  operational_state:
    driver: postgresql

mxm_paths:
  data_root: 123
  artifact_root: /tmp/mxm/artifacts
  export_root: /tmp/mxm/exports
  log_root: /tmp/mxm/logs
""",
        encoding="utf-8",
    )
    return tmp_path


def _write_minimal_config_store(
    tmp_path: Path,
    *,
    capability_config: str,
) -> Path:
    """Write path config plus the supplied optional capability config."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)
    (app_root / "default.yaml").write_text(
        f"""\
{capability_config}
mxm_paths:
  data_root: /tmp/mxm/data
  artifact_root: /tmp/mxm/artifacts
  export_root: /tmp/mxm/exports
  log_root: /tmp/mxm/logs
""",
        encoding="utf-8",
    )
    return tmp_path
