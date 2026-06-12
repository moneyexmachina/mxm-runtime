"""Tests for RuntimeContext materialisation."""

from __future__ import annotations

from pathlib import Path

import pytest

from mxm.runtime.build import build_runtime_context
from mxm.types import RuntimeIdentity


def test_build_runtime_context_materialises_secrets_api(
    tmp_path: Path,
) -> None:
    """build_runtime_context should construct a configured SecretsApi."""
    store_root = _write_config_store(tmp_path)
    identity = _identity(machine="bridge")

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


def test_build_runtime_context_applies_machine_specific_store_config(
    tmp_path: Path,
) -> None:
    """Machine-specific config should determine available secret stores."""
    store_root = _write_config_store(tmp_path)

    bridge_context = build_runtime_context(
        identity=_identity(machine="bridge"),
        store_root=store_root,
    )
    monolith_context = build_runtime_context(
        identity=_identity(machine="monolith"),
        store_root=store_root,
    )

    assert bridge_context.secrets is not None
    assert monolith_context.secrets is not None

    assert bridge_context.secrets.secret_store_registry.contains("red")
    assert bridge_context.secrets.secret_store_registry.contains("black")

    assert monolith_context.secrets.secret_store_registry.contains("red")
    assert not monolith_context.secrets.secret_store_registry.contains("black")


def test_build_runtime_context_rejects_missing_mxm_secrets_section(
    tmp_path: Path,
) -> None:
    """build_runtime_context should require an mxm_secrets config section."""
    store_root = _write_config_store_without_mxm_secrets(tmp_path)

    with pytest.raises(KeyError, match="mxm_secrets"):
        build_runtime_context(
            identity=_identity(machine="bridge"),
            store_root=store_root,
        )


def test_build_runtime_context_propagates_invalid_secret_store_config(
    tmp_path: Path,
) -> None:
    """build_runtime_context should propagate mxm-secrets config errors."""
    store_root = _write_config_store_with_invalid_store(tmp_path)

    with pytest.raises(TypeError, match="Secret store config"):
        build_runtime_context(
            identity=_identity(machine="bridge"),
            store_root=store_root,
        )


def _identity(*, machine: str) -> RuntimeIdentity:
    """Return a test runtime identity for mxm-secrets config loading."""
    return RuntimeIdentity(
        app="mxm-secrets",
        environment="dev",
        machine=machine,
        substrate="local-process",
        role="marketdata",
    )


def _write_config_store(tmp_path: Path) -> Path:
    """Write a temporary mxm-config-store with mxm-secrets configuration."""
    app_root = tmp_path / "apps" / "mxm-secrets"
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
""",
        encoding="utf-8",
    )

    (app_root / "machine.yaml").write_text(
        """\
bridge:
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

monolith:
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
""",
        encoding="utf-8",
    )

    return tmp_path


def _write_config_store_without_mxm_secrets(tmp_path: Path) -> Path:
    """Write a temporary config store missing the mxm_secrets section."""
    app_root = tmp_path / "apps" / "mxm-secrets"
    app_root.mkdir(parents=True)

    (app_root / "default.yaml").write_text(
        """\
other_package:
  enabled: true
""",
        encoding="utf-8",
    )

    return tmp_path


def _write_config_store_with_invalid_store(tmp_path: Path) -> Path:
    """Write a temporary config store with invalid secret store config."""
    app_root = tmp_path / "apps" / "mxm-secrets"
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
