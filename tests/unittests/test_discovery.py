"""Tests for runtime discovery helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from mxm.runtime.discovery import discover_machine, discover_substrate


def _wildling_hostname() -> str:
    return "wildling"


def test_discover_machine_uses_system_hostname(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mxm.runtime.discovery.socket.gethostname",
        _wildling_hostname,
    )

    assert discover_machine() == "wildling"


def test_discover_substrate_detects_docker_container(
    tmp_path: Path,
) -> None:
    dockerenv_path = tmp_path / ".dockerenv"
    dockerenv_path.touch()

    assert (
        discover_substrate(
            dockerenv_path=dockerenv_path,
        )
        == "docker-container"
    )


def test_discover_substrate_defaults_to_local_process(
    tmp_path: Path,
) -> None:
    dockerenv_path = tmp_path / ".dockerenv"

    assert (
        discover_substrate(
            dockerenv_path=dockerenv_path,
        )
        == "local-process"
    )
