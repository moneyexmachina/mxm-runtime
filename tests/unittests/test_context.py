"""Tests for the public RuntimeContext contract."""

from __future__ import annotations

from dataclasses import MISSING, fields
from pathlib import Path

import mxm.runtime as runtime_package
import mxm.runtime.build as runtime_build
import mxm.runtime.context as context_module
from mxm.config import make_subconfig
from mxm.runtime.context import RuntimeContext, RuntimePaths
from mxm.types import RuntimeIdentity


def test_runtime_paths_retains_explicit_paths() -> None:
    """RuntimePaths should retain explicitly supplied path values."""
    paths = RuntimePaths(
        data_root=Path("/var/lib/mxm/data"),
        artifact_root=Path("/var/lib/mxm/artifacts"),
        export_root=Path("/var/lib/mxm/exports"),
        log_root=Path("/var/log/mxm"),
    )

    assert paths.data_root == Path("/var/lib/mxm/data")
    assert paths.artifact_root == Path("/var/lib/mxm/artifacts")
    assert paths.export_root == Path("/var/lib/mxm/exports")
    assert paths.log_root == Path("/var/log/mxm")


def test_runtime_context_has_exactly_three_mandatory_fields() -> None:
    """RuntimeContext should require only identity, config, and paths."""
    context_fields = fields(RuntimeContext)

    assert tuple(field.name for field in context_fields) == (
        "identity",
        "config",
        "paths",
    )
    assert all(field.default is MISSING for field in context_fields)
    assert all(field.default_factory is MISSING for field in context_fields)


def test_runtime_context_retains_complete_resolved_context() -> None:
    """RuntimeContext should retain all three integration values."""
    identity = RuntimeIdentity(
        app="mxm_moneymachine",
        environment="dev",
        machine="bridge",
        substrate="local_process",
        role="research",
    )
    config = make_subconfig({"application": {"name": "moneymachine"}})
    paths = RuntimePaths(
        data_root=Path("/var/lib/mxm/data"),
        artifact_root=Path("/var/lib/mxm/artifacts"),
        export_root=Path("/var/lib/mxm/exports"),
        log_root=Path("/var/log/mxm"),
    )

    context = RuntimeContext(identity=identity, config=config, paths=paths)

    assert context.identity == identity
    assert context.config is config
    assert context.paths == paths


def test_removed_context_models_and_fields_are_not_public() -> None:
    """Removed capability and metadata surfaces should not remain public."""
    assert not hasattr(context_module, "RuntimeMetadata")

    for removed_field in ("secrets", "db_configs", "runtime"):
        assert not hasattr(RuntimeContext, removed_field)


def test_runtime_package_exports_the_accepted_public_contract() -> None:
    """The package should export resolution without removed public names."""
    assert set(runtime_package.__all__) == {
        "RuntimeContext",
        "RuntimeIdentity",
        "RuntimeIdentityError",
        "RuntimePaths",
        "build_runtime_identity",
        "resolve_runtime_context",
        "validate_runtime_identity_shape",
    }
    package_resolver = getattr(runtime_package, "resolve_runtime_context", None)
    build_resolver = getattr(runtime_build, "resolve_runtime_context", None)
    assert callable(package_resolver)
    assert package_resolver is build_resolver

    for removed_name in ("RuntimeMetadata", "build_runtime_context"):
        assert not hasattr(runtime_package, removed_name)
        assert not hasattr(runtime_build, removed_name)
