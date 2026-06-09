"""Tests for runtime identity attestation."""

from __future__ import annotations

import pytest

from mxm.runtime.attestation import (
    RuntimeIdentityAttestationError,
    attest_runtime_identity,
)
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


def _bridge_machine() -> MachineId:
    return MachineId("bridge")


def _wildling_machine() -> MachineId:
    return MachineId("wildling")


def _local_process() -> RuntimeSubstrate:
    return RuntimeSubstrate("local-process")


def _docker_container() -> RuntimeSubstrate:
    return RuntimeSubstrate("docker-container")


def test_attest_runtime_identity_accepts_matching_local_facts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mxm.runtime.attestation.discover_machine", _bridge_machine)
    monkeypatch.setattr("mxm.runtime.attestation.discover_substrate", _local_process)

    attest_runtime_identity(_identity())


def test_attest_runtime_identity_rejects_machine_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mxm.runtime.attestation.discover_machine", _wildling_machine)
    monkeypatch.setattr("mxm.runtime.attestation.discover_substrate", _local_process)

    with pytest.raises(RuntimeIdentityAttestationError, match="machine"):
        attest_runtime_identity(_identity())


def test_attest_runtime_identity_rejects_substrate_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mxm.runtime.attestation.discover_machine", _bridge_machine)
    monkeypatch.setattr("mxm.runtime.attestation.discover_substrate", _docker_container)

    with pytest.raises(RuntimeIdentityAttestationError, match="substrate"):
        attest_runtime_identity(_identity())


def test_attest_runtime_identity_reports_both_mismatches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mxm.runtime.attestation.discover_machine", _wildling_machine)
    monkeypatch.setattr("mxm.runtime.attestation.discover_substrate", _docker_container)

    with pytest.raises(RuntimeIdentityAttestationError) as exc_info:
        attest_runtime_identity(_identity())

    message = str(exc_info.value)

    assert "machine" in message
    assert "substrate" in message


def test_attest_runtime_identity_does_not_attest_invocation_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mxm.runtime.attestation.discover_machine", _bridge_machine)
    monkeypatch.setattr("mxm.runtime.attestation.discover_substrate", _local_process)

    attest_runtime_identity(
        _identity(
            app="unknown-app",
            environment="unknown-environment",
            role="unknown-role",
        )
    )
