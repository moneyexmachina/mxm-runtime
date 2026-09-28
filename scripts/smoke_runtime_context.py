"""Local smoke script for RuntimeContext resolution.

This script exercises the local runtime resolution chain:

RuntimeIdentity
    ↓
mxm-config
    ↓
RuntimeContext

It is intentionally not a test. It depends on the local mxm-config-store.

Run from the repository root with:

```bash
poetry run python scripts/smoke_runtime_context.py
```
"""

from __future__ import annotations

from mxm.runtime.build import resolve_runtime_context
from mxm.runtime.discovery import discover_machine, discover_substrate
from mxm.types import RuntimeIdentity


def main() -> None:
    """Resolve and print a local RuntimeContext smoke summary."""
    machine = discover_machine()
    substrate = discover_substrate()

    identity = RuntimeIdentity(
        app="mxm-runtime",
        environment="dev",
        machine=machine,
        substrate=substrate,
        role="marketdata",
    )

    context = resolve_runtime_context(identity=identity)

    print("RuntimeContext resolved")
    print()
    print("Identity")
    print(f"  app:         {context.identity.app}")
    print(f"  environment: {context.identity.environment}")
    print(f"  machine:     {context.identity.machine}")
    print(f"  substrate:   {context.identity.substrate}")
    print(f"  role:        {context.identity.role}")
    print()

    print("Paths")
    print(f"  data:        {context.paths.data_root}")
    print(f"  artifacts:   {context.paths.artifact_root}")
    print(f"  exports:     {context.paths.export_root}")
    print(f"  logs:        {context.paths.log_root}")


if __name__ == "__main__":
    main()
