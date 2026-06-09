"""Runtime identity attestation.

Attestation checks whether the empirical claims in a RuntimeIdentity match the
current running process.

This is distinct from shape validation. Shape validation checks whether an
identity object is well formed. Attestation checks whether selected claims are
true here.
"""

from __future__ import annotations

from mxm.runtime.discovery import discover_machine, discover_substrate
from mxm.types import RuntimeIdentity


class RuntimeIdentityAttestationError(RuntimeError):
    """Raised when a runtime identity is not true for this process."""


def attest_runtime_identity(identity: RuntimeIdentity) -> None:
    """Attest that empirical RuntimeIdentity claims match local discovery.

    Only locally discoverable empirical fields are attested:

    - ``machine``
    - ``substrate``

    The following fields are not attested here because they are invocation or
    deployment claims rather than directly discoverable local facts:

    - ``app``
    - ``environment``
    - ``role``
    """
    discovered_machine = discover_machine()
    discovered_substrate = discover_substrate()

    errors: list[str] = []

    if identity.machine != discovered_machine:
        errors.append(
            "machine claim does not match local discovery: "
            f"identity.machine={identity.machine!r}, "
            f"discovered_machine={discovered_machine!r}"
        )

    if identity.substrate != discovered_substrate:
        errors.append(
            "substrate claim does not match local discovery: "
            f"identity.substrate={identity.substrate!r}, "
            f"discovered_substrate={discovered_substrate!r}"
        )

    if errors:
        message = "; ".join(errors)
        raise RuntimeIdentityAttestationError(message)
