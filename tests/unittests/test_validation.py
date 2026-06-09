"""Tests for runtime identity validation."""

from __future__ import annotations

import pytest

from mxm.runtime.validation import RuntimeIdentityError, validate_runtime_identity_shape
from mxm.types import (
    AppId,
    Environment,
    MachineId,
    RuntimeIdentity,
    RuntimeRole,
    RuntimeSubstrate,
)


def _identity(
    *,
    app: str = "mxm-moneymachine",
    environment: str = "dev",
    machine: str = "bridge",
    substrate: str = "local-process",
    role: str = "research",
) -> RuntimeIdentity:
    return RuntimeIdentity(
        app=AppId(app),
        environment=Environment(environment),
        machine=MachineId(machine),
        substrate=RuntimeSubstrate(substrate),
        role=RuntimeRole(role),
    )


def test_validate_runtime_identity_accepts_valid_identity() -> None:
    validate_runtime_identity_shape(_identity())


@pytest.mark.parametrize(
    ("field_name", "identity"),
    [
        ("app", _identity(app="")),
        ("environment", _identity(environment="")),
        ("machine", _identity(machine="")),
        ("substrate", _identity(substrate="")),
        ("role", _identity(role="")),
    ],
)
def test_validate_runtime_identity_rejects_empty_required_fields(
    field_name: str,
    identity: RuntimeIdentity,
) -> None:
    with pytest.raises(RuntimeIdentityError, match=field_name):
        validate_runtime_identity_shape(identity)


@pytest.mark.parametrize(
    ("field_name", "identity"),
    [
        ("app", _identity(app="   ")),
        ("environment", _identity(environment="\t")),
        ("machine", _identity(machine="\n")),
        ("substrate", _identity(substrate="  \t  ")),
        ("role", _identity(role="  \n  ")),
    ],
)
def test_validate_runtime_identity_rejects_whitespace_only_required_fields(
    field_name: str,
    identity: RuntimeIdentity,
) -> None:
    with pytest.raises(RuntimeIdentityError, match=field_name):
        validate_runtime_identity_shape(identity)


def test_validate_runtime_identity_error_names_all_missing_fields() -> None:
    identity = _identity(
        app="",
        environment="",
        machine="",
        substrate="",
        role="",
    )

    with pytest.raises(RuntimeIdentityError) as exc_info:
        validate_runtime_identity_shape(identity)

    message = str(exc_info.value)

    assert "app" in message
    assert "environment" in message
    assert "machine" in message
    assert "substrate" in message
    assert "role" in message
