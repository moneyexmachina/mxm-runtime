"""Tests for runtime identity construction."""

from __future__ import annotations

import pytest

from mxm.runtime.identity import build_runtime_identity
from mxm.runtime.validation import RuntimeIdentityError
from mxm.types import (
    RuntimeIdentity,
)


def _discovered_machine() -> str:
    return "bridge"


def _discovered_substrate() -> str:
    return "local-process"


def test_build_runtime_identity_with_explicit_values() -> None:
    identity = build_runtime_identity(
        app="mxm-moneymachine",
        environment="dev",
        machine="bridge",
        substrate="local-process",
        role="research",
    )

    assert identity == RuntimeIdentity(
        app="mxm-moneymachine",
        environment="dev",
        machine="bridge",
        substrate="local-process",
        role="research",
    )


def test_build_runtime_identity_discovers_missing_machine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mxm.runtime.identity.discover_machine",
        _discovered_machine,
    )

    identity = build_runtime_identity(
        app="mxm-moneymachine",
        environment="dev",
        substrate="local-process",
        role="research",
    )

    assert identity.machine == "bridge"


def test_build_runtime_identity_discovers_missing_substrate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mxm.runtime.identity.discover_substrate",
        _discovered_substrate,
    )

    identity = build_runtime_identity(
        app="mxm-moneymachine",
        environment="dev",
        machine="bridge",
        role="research",
    )

    assert identity.substrate == "local-process"


def test_build_runtime_identity_discovers_missing_machine_and_substrate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mxm.runtime.identity.discover_machine",
        _discovered_machine,
    )
    monkeypatch.setattr(
        "mxm.runtime.identity.discover_substrate",
        _discovered_substrate,
    )

    identity = build_runtime_identity(
        app="mxm-moneymachine",
        environment="dev",
        role="research",
    )

    assert identity == RuntimeIdentity(
        app="mxm-moneymachine",
        environment="dev",
        machine="bridge",
        substrate="local-process",
        role="research",
    )


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    [
        ("app", {"app": ""}),
        ("environment", {"environment": ""}),
        ("machine", {"machine": ""}),
        ("substrate", {"substrate": ""}),
        ("role", {"role": ""}),
    ],
)
def test_build_runtime_identity_rejects_invalid_constructed_identity(
    field_name: str,
    kwargs: dict[str, str],
) -> None:
    values = {
        "app": "mxm-moneymachine",
        "environment": "dev",
        "machine": "bridge",
        "substrate": "local-process",
        "role": "research",
    }
    values.update(kwargs)

    with pytest.raises(RuntimeIdentityError, match=field_name):
        build_runtime_identity(
            app=values["app"],
            environment=values["environment"],
            machine=values["machine"],
            substrate=values["substrate"],
            role=values["role"],
        )
