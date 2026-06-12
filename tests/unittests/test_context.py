"""Tests for mxm.runtime context model objects."""

from __future__ import annotations

from pathlib import Path

from mxm.config import make_subconfig
from mxm.runtime.context import (
    RuntimeContext,
    RuntimeMetadata,
    RuntimePaths,
)
from mxm.secrets import SecretsApi
from mxm.secrets.registries import (
    SecretPolicyRegistry,
    SecretRefRegistry,
    SecretStoreRegistry,
)
from mxm.types import RuntimeIdentity


def test_runtime_paths_defaults_to_none() -> None:
    """RuntimePaths should default all optional roots to None."""
    paths = RuntimePaths()

    assert paths.data_root is None
    assert paths.artifact_root is None
    assert paths.state_root is None
    assert paths.log_root is None


def test_runtime_paths_retains_explicit_paths() -> None:
    """RuntimePaths should retain explicitly supplied path values."""
    paths = RuntimePaths(
        data_root=Path("/var/lib/mxm/data"),
        artifact_root=Path("/var/lib/mxm/artifacts"),
        state_root=Path("/var/lib/mxm/state"),
        log_root=Path("/var/log/mxm"),
    )

    assert paths.data_root == Path("/var/lib/mxm/data")
    assert paths.artifact_root == Path("/var/lib/mxm/artifacts")
    assert paths.state_root == Path("/var/lib/mxm/state")
    assert paths.log_root == Path("/var/log/mxm")


def test_runtime_metadata_retains_execution_metadata() -> None:
    """RuntimeMetadata should retain materialised substrate metadata."""
    metadata = RuntimeMetadata(
        substrate="local_process",
        is_container=False,
    )

    assert metadata.substrate == "local_process"
    assert metadata.is_container is False


def test_runtime_context_supports_minimal_construction() -> None:
    """RuntimeContext should support construction with only core fields."""
    identity = RuntimeIdentity(
        app="mxm_moneymachine",
        environment="dev",
        machine="bridge",
        substrate="local_process",
        role="research",
    )
    config = make_subconfig(
        {
            "mxm_secrets": {
                "stores": {},
                "refs": {},
                "policies": {},
            },
        }
    )

    context = RuntimeContext(
        identity=identity,
        config=config,
    )

    assert context.identity == identity
    assert context.config is config
    assert context.secrets is None
    assert context.paths is None
    assert context.runtime is None


def test_runtime_context_supports_full_construction() -> None:
    """RuntimeContext should retain all materialised context components."""
    identity = RuntimeIdentity(
        app="mxm_moneymachine",
        environment="dev",
        machine="bridge",
        substrate="local_process",
        role="research",
    )
    config = make_subconfig(
        {
            "mxm_secrets": {
                "stores": {},
                "refs": {},
                "policies": {},
            },
        }
    )
    secrets = SecretsApi(
        secret_ref_registry=SecretRefRegistry(()),
        secret_store_registry=SecretStoreRegistry(()),
        secret_policy_registry=SecretPolicyRegistry(()),
    )
    paths = RuntimePaths(
        data_root=Path("/var/lib/mxm/data"),
        artifact_root=Path("/var/lib/mxm/artifacts"),
        state_root=Path("/var/lib/mxm/state"),
        log_root=Path("/var/log/mxm"),
    )
    runtime = RuntimeMetadata(
        substrate="local_process",
        is_container=False,
    )

    context = RuntimeContext(
        identity=identity,
        config=config,
        secrets=secrets,
        paths=paths,
        runtime=runtime,
    )

    assert context.identity == identity
    assert context.config is config
    assert context.secrets is secrets
    assert context.paths == paths
    assert context.runtime == runtime
