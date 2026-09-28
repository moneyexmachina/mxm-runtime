# mxm-runtime

![Version](https://img.shields.io/github/v/release/moneyexmachina/mxm-runtime)
![License](https://img.shields.io/github/license/moneyexmachina/mxm-runtime)
![Python](https://img.shields.io/badge/python-3.13+-blue)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Runtime identity discovery and context resolution for the Money Ex Machina
ecosystem.

`mxm-runtime` discovers runtime characteristics and resolves the shared context
that applications use during composition. It does not construct
capability-specific services.

## RuntimeContext

`RuntimeContext` is the complete integration protocol between runtime
resolution and application composition. It contains exactly three mandatory
values:

```python
RuntimeContext(
    identity=...,
    config=...,
    paths=...,
)
```

- `identity` is the resolved `RuntimeIdentity`.
- `config` is the complete identity-selected `MXMConfig`.
- `paths` contains the resolved data, artifact, export, and log roots.

A successfully resolved context is complete, but does not claim that downstream
capabilities are authenticated, connected, or ready.

## Resolution flow

```text
RuntimeIdentity
    ↓
mxm-config
    ↓
Identity-selected configuration
    ↓
RuntimePaths resolution
    ↓
RuntimeContext
    ↓
Application composition
```

Runtime identity selects application, environment, and machine configuration
layers. The `mxm_paths` namespace is runtime-owned and is resolved into
`RuntimePaths`.

Other namespaces, including `mxm_secrets` and `mxm_databases`, remain available
unchanged through `context.config`. Their owning packages validate and
interpret them when the application composes those capabilities.

## Runtime identity and discovery

`RuntimeIdentity` represents the operational identity of a process:

```text
app          mxm-moneymachine
environment  dev
machine      bridge
substrate    local-process
role         marketdata
```

Machine and substrate discovery utilities derive selectors from operating
system facts:

```python
from mxm.runtime.discovery import discover_machine, discover_substrate

machine = discover_machine()
substrate = discover_substrate()
```

Machine values select machine-specific configuration. They are not unique
hardware identifiers.

## Usage

```python
from mxm.runtime import resolve_runtime_context

context = resolve_runtime_context(identity=identity)

data_root = context.paths.data_root
database_config = context.config.mxm_databases.operational_state
secrets_config = context.config.mxm_secrets
```

Applications pass capability configuration to the package that owns that
capability. `mxm-runtime` does not construct a `SecretsApi`, database clients,
or other capability object graphs.

For tests or alternate configuration stores, pass an explicit store root:

```python
context = resolve_runtime_context(
    identity=identity,
    store_root=config_store_path,
)
```

Resolution requires valid identity-selected configuration and an `mxm_paths`
namespace with string values for:

```text
data_root
artifact_root
export_root
log_root
```

Missing or capability-invalid `mxm_secrets` and `mxm_databases` namespaces do
not prevent runtime context resolution.

## Ownership boundaries

`mxm-runtime` owns:

- runtime identity discovery and validation;
- identity-selected configuration loading;
- runtime path resolution;
- `RuntimeContext` assembly.

`mxm-config` owns configuration storage, loading, merging, views, and
interpolation.

Capability packages own their configuration schemas, validation, and service
composition. This keeps objects produced by application composition out of the
context used for application composition.

## Installation

```bash
pip install mxm-runtime
```

## Development

```bash
poetry install
make check
```

Run the local RuntimeContext smoke script:

```bash
poetry run python scripts/smoke_runtime_context.py
```

The smoke script depends on a local `mxm-config-store`.

## License

MIT License. See [LICENSE](LICENSE).
