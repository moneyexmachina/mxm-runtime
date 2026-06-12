"""Local smoke script for RuntimeContext materialisation.

This script exercises the local runtime materialisation chain:

RuntimeIdentity
    ↓
mxm-config
    ↓
mxm-secrets
    ↓
RuntimeContext

It is intentionally not a test. It depends on local machine state, including the
local mxm-config-store and gopass installation.

Run from the repository root with:

```bash
poetry run python scripts/smoke_runtime_context.py
```
"""

from __future__ import annotations

from mxm.runtime.build import build_runtime_context
from mxm.runtime.discovery import discover_machine, discover_substrate
from mxm.types import RuntimeIdentity


def main() -> None:
    """Build and print a local RuntimeContext smoke summary."""
    machine = discover_machine()
    substrate = discover_substrate()

    identity = RuntimeIdentity(
        app="mxm-secrets",
        environment="dev",
        machine=machine,
        substrate=substrate,
        role="marketdata",
    )

    context = build_runtime_context(identity=identity)

    print("RuntimeContext materialised")
    print()
    print("Identity")
    print(f"  app:         {context.identity.app}")
    print(f"  environment: {context.identity.environment}")
    print(f"  machine:     {context.identity.machine}")
    print(f"  substrate:   {context.identity.substrate}")
    print(f"  role:        {context.identity.role}")
    print()

    if context.secrets is None:
        raise RuntimeError("RuntimeContext.secrets was not materialised")

    print("Secrets")
    print(f"  stores:      {', '.join(context.secrets.secret_store_registry.names())}")
    print(f"  refs:        {', '.join(context.secrets.secret_ref_registry.names())}")
    print(f"  policies:    {', '.join(context.secrets.secret_policy_registry.names())}")
    print(f"  gopass ready: {context.secrets.check_ready()}")


if __name__ == "__main__":
    main()
