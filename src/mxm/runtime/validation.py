"""Runtime identity validation."""

from __future__ import annotations

from mxm.types import RuntimeIdentity


class RuntimeIdentityError(ValueError):
    """Raised when a runtime identity is invalid."""


def validate_runtime_identity_shape(identity: RuntimeIdentity) -> None:
    """Validate a RuntimeIdentity.

    Validation is intentionally minimal for v0.1.0. Policy-specific allowed
    values should be introduced only once the deployment model has stabilized.
    """
    fields = {
        "app": identity.app,
        "environment": identity.environment,
        "machine": identity.machine,
        "substrate": identity.substrate,
        "role": identity.role,
    }

    missing = [name for name, value in fields.items() if not str(value).strip()]

    if missing:
        joined = ", ".join(missing)
        raise RuntimeIdentityError(
            f"RuntimeIdentity contains empty required field(s): {joined}"
        )
