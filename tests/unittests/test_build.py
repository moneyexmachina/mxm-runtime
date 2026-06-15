"""Tests for RuntimeContext materialisation."""

from __future__ import annotations

from pathlib import Path

import pytest

from mxm.runtime.build import build_runtime_context
from mxm.types import RuntimeIdentity


def test_build_runtime_context_materialises_runtime_resources(
    tmp_path: Path,
) -> None:
    """build_runtime_context should construct configured runtime resources."""
    store_root = _write_config_store(tmp_path)
    identity = _identity(machine="bridge", environment="dev")

    context = build_runtime_context(
        identity=identity,
        store_root=store_root,
    )

    assert context.identity == identity
    assert context.config is not None

    assert context.secrets is not None
    assert context.secrets.secret_ref_registry.contains("databento_api_key")
    assert context.secrets.secret_store_registry.contains("red")
    assert context.secrets.secret_policy_registry.contains("marketdata_access")

    assert context.db_configs is not None
    assert context.db_configs.operational_state.driver == "postgresql"
    assert context.db_configs.operational_state.host == "localhost"
    assert context.db_configs.operational_state.port == 5432
    assert context.db_configs.operational_state.name == "mxm_dev"
    assert context.db_configs.operational_state.user == "mxm_dev_app"
    assert context.db_configs.operational_state.password_ref == "mxm_dev_db_password"

    assert context.paths is not None
    assert context.paths.data_root == Path("~/.mxm/dev/data").expanduser()
    assert context.paths.artifact_root == Path("~/.mxm/dev/artifacts").expanduser()
    assert context.paths.export_root == Path("~/.mxm/dev/exports").expanduser()
    assert context.paths.log_root == Path("~/.mxm/dev/logs").expanduser()


def test_build_runtime_context_applies_machine_specific_store_config(
    tmp_path: Path,
) -> None:
    """Machine-specific config should determine available secret stores."""
    store_root = _write_config_store(tmp_path)

    bridge_context = build_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=store_root,
    )
    monolith_context = build_runtime_context(
        identity=_identity(machine="monolith", environment="prod"),
        store_root=store_root,
    )

    assert bridge_context.secrets is not None
    assert monolith_context.secrets is not None

    assert bridge_context.secrets.secret_store_registry.contains("red")
    assert bridge_context.secrets.secret_store_registry.contains("black")

    assert monolith_context.secrets.secret_store_registry.contains("red")
    assert not monolith_context.secrets.secret_store_registry.contains("black")


def test_build_runtime_context_resolves_machine_and_environment_paths(
    tmp_path: Path,
) -> None:
    """Machine and environment config should jointly resolve runtime paths."""
    store_root = _write_config_store(tmp_path)

    bridge_dev_context = build_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=store_root,
    )
    monolith_prod_context = build_runtime_context(
        identity=_identity(machine="monolith", environment="prod"),
        store_root=store_root,
    )

    assert bridge_dev_context.paths is not None
    assert monolith_prod_context.paths is not None

    assert bridge_dev_context.paths.data_root == Path("~/.mxm/dev/data").expanduser()
    assert (
        bridge_dev_context.paths.artifact_root
        == Path("~/.mxm/dev/artifacts").expanduser()
    )
    assert (
        bridge_dev_context.paths.export_root == Path("~/.mxm/dev/exports").expanduser()
    )
    assert bridge_dev_context.paths.log_root == Path("~/.mxm/dev/logs").expanduser()

    assert monolith_prod_context.paths.data_root == Path("/srv/mxm/prod/data")
    assert monolith_prod_context.paths.artifact_root == Path("/srv/mxm/prod/artifacts")
    assert monolith_prod_context.paths.export_root == Path("/srv/mxm/prod/exports")
    assert monolith_prod_context.paths.log_root == Path("/srv/mxm/prod/logs")


def test_build_runtime_context_resolves_environment_specific_database_config(
    tmp_path: Path,
) -> None:
    """Environment config should determine database identity."""
    store_root = _write_config_store(tmp_path)

    dev_context = build_runtime_context(
        identity=_identity(machine="bridge", environment="dev"),
        store_root=store_root,
    )
    prod_context = build_runtime_context(
        identity=_identity(machine="monolith", environment="prod"),
        store_root=store_root,
    )

    assert dev_context.db_configs is not None
    assert prod_context.db_configs is not None

    assert dev_context.db_configs.operational_state.name == "mxm_dev"
    assert dev_context.db_configs.operational_state.user == "mxm_dev_app"
    assert (
        dev_context.db_configs.operational_state.password_ref == "mxm_dev_db_password"
    )

    assert prod_context.db_configs.operational_state.name == "mxm_prod"
    assert prod_context.db_configs.operational_state.user == "mxm_prod_app"
    assert (
        prod_context.db_configs.operational_state.password_ref == "mxm_prod_db_password"
    )


def test_build_runtime_context_rejects_missing_mxm_secrets_section(
    tmp_path: Path,
) -> None:
    """build_runtime_context should require an mxm_secrets config section."""
    store_root = _write_config_store_without_mxm_secrets(tmp_path)

    with pytest.raises(KeyError, match="mxm_secrets"):
        build_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=store_root,
        )


def test_build_runtime_context_rejects_missing_mxm_databases_section(
    tmp_path: Path,
) -> None:
    """build_runtime_context should require an mxm_databases config section."""
    store_root = _write_config_store_without_mxm_databases(tmp_path)

    with pytest.raises(KeyError, match="mxm_databases"):
        build_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=store_root,
        )


def test_build_runtime_context_rejects_missing_mxm_paths_section(
    tmp_path: Path,
) -> None:
    """build_runtime_context should require an mxm_paths config section."""
    store_root = _write_config_store_without_mxm_paths(tmp_path)

    with pytest.raises(KeyError, match="mxm_paths"):
        build_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=store_root,
        )


def test_build_runtime_context_propagates_invalid_secret_store_config(
    tmp_path: Path,
) -> None:
    """build_runtime_context should propagate mxm-secrets config errors."""
    store_root = _write_config_store_with_invalid_store(tmp_path)

    with pytest.raises(TypeError, match="Secret store config"):
        build_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=store_root,
        )


def test_build_runtime_context_rejects_invalid_path_config(
    tmp_path: Path,
) -> None:
    """build_runtime_context should reject non-string path values."""
    store_root = _write_config_store_with_invalid_paths(tmp_path)

    with pytest.raises(TypeError, match="data_root"):
        build_runtime_context(
            identity=_identity(machine="bridge", environment="dev"),
            store_root=store_root,
        )


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

    mxm_dev_db_password:
      store: red
      path: infra/postgres/mxm_dev_app/password
      policy: database_access

    mxm_prod_db_password:
      store: red
      path: infra/postgres/mxm_prod_app/password
      policy: database_access

  policies:
    marketdata_access:
      allowed_principals:
        - marketdata
        - research

    database_access:
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
      user: mxm_dev_app
      password_ref: mxm_dev_db_password

prod:
  mxm_environment:
    name: prod

  mxm_databases:
    operational_state:
      name: mxm_prod
      user: mxm_prod_app
      password_ref: mxm_prod_db_password
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
      green:
        backend: gopass
        root: mxm/green
      yellow:
        backend: gopass
        root: mxm/yellow
      red:
        backend: gopass
        root: mxm/red
      black:
        backend: gopass
        root: mxm/black

  mxm_databases:
    operational_state:
      host: localhost
      port: 5432

monolith:
  mxm_machine:
    root: /srv/mxm

  mxm_secrets:
    stores:
      green:
        backend: gopass
        root: mxm/green
      yellow:
        backend: gopass
        root: mxm/yellow
      red:
        backend: gopass
        root: mxm/red

  mxm_databases:
    operational_state:
      host: localhost
      port: 5432
""",
        encoding="utf-8",
    )

    return tmp_path


def _write_config_store_without_mxm_secrets(tmp_path: Path) -> Path:
    """Write a temporary config store missing the mxm_secrets section."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)

    (app_root / "default.yaml").write_text(
        """\
mxm_databases:
  operational_state:
    driver: postgresql

mxm_paths:
  data_root: /tmp/mxm/data
  artifact_root: /tmp/mxm/artifacts
  export_root: /tmp/mxm/exports
  log_root: /tmp/mxm/logs
""",
        encoding="utf-8",
    )

    return tmp_path


def _write_config_store_without_mxm_databases(tmp_path: Path) -> Path:
    """Write a temporary config store missing the mxm_databases section."""
    app_root = tmp_path / "apps" / "mxm-runtime-test"
    app_root.mkdir(parents=True)

    (app_root / "default.yaml").write_text(
        """\
mxm_secrets:
  stores: {}
  refs: {}
  policies: {}

mxm_paths:
  data_root: /tmp/mxm/data
  artifact_root: /tmp/mxm/artifacts
  export_root: /tmp/mxm/exports
  log_root: /tmp/mxm/logs
""",
        encoding="utf-8",
    )

    return tmp_path


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
    """Write a temporary config store with invalid secret store config."""
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

mxm_databases:
  operational_state:
    driver: postgresql

mxm_paths:
  data_root: /tmp/mxm/data
  artifact_root: /tmp/mxm/artifacts
  export_root: /tmp/mxm/exports
  log_root: /tmp/mxm/logs
""",
        encoding="utf-8",
    )

    (app_root / "machine.yaml").write_text(
        """\
bridge:
  mxm_secrets:
    stores:
      red: not-a-mapping
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
