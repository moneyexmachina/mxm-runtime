# mxm-runtime

![Version](https://img.shields.io/github/v/release/moneyexmachina/mxm-runtime)
![License](https://img.shields.io/github/license/moneyexmachina/mxm-runtime)
![Python](https://img.shields.io/badge/python-3.13+-blue)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Runtime discovery, configuration-driven runtime resource materialization, and RuntimeContext assembly for the Money Ex Machina ecosystem.

`mxm-runtime` is responsible for constructing the operational environment in which MXM applications execute.

It discovers runtime characteristics, loads and resolves configuration, constructs configured services, and assembles them into a single RuntimeContext.

## Purpose

MXM applications require more than configuration files.

They require an operational environment:

```text
Who am I?
Where am I running?
Which configuration applies?
Which services are available?
Where should data and artefacts live?
```

`mxm-runtime` answers these questions.

It exists to separate:

```text
application code
```

from:

```text
runtime discovery
configuration loading
service construction
deployment concerns
context assembly
```

Applications should not:

- discover machine characteristics,
- determine deployment substrate,
- load configuration directly,
- construct service APIs,
- or reason about deployment topology.

Instead, applications receive a configured RuntimeContext:

```python
context = build_runtime_context(
    identity=runtime_identity,
)
```

and consume the services and resources provided by that context.

## Architecture

`mxm-runtime` acts as the runtime constructor layer of the MXM architecture.

```text
RuntimeIdentity
    ↓
mxm-config
    ↓
Configuration Resolution
    ↓
Resource Materialisation
    ↓
RuntimeContext
    ↓
Application
```

The package owns runtime construction.

It does not own configuration semantics or secret resolution semantics.

Those responsibilities belong to:

```text
mxm-config
```

and:

```text
mxm-secrets
```

respectively.

## Core Concepts

### RuntimeIdentity

Represents the operational identity of a running process.

Example:

```text
app          mxm-moneymachine
environment  dev
machine      bridge
substrate    local-process
role         marketdata
```

Runtime identity determines which configuration layers are selected and which services are constructed.

### Machine

A machine identifies a machine-specific configuration profile.

Examples:

```text
bridge
monolith
wildling
scribe
```

Machine values are derived from operating-system characteristics and are used to select machine-specific configuration.

They are configuration selectors rather than unique hardware identifiers.

### Substrate

Represents the execution substrate.

Examples:

```text
local-process
docker
```

Substrate allows runtime construction to adapt to deployment environment differences.

### RuntimeContext

Represents the fully constructed operational environment.

Current fields:

```python
RuntimeContext(
    identity=...,
    config=...,
    secrets=...,
    db_configs=...,
    paths=...,
    runtime=...,
)
```
Current RuntimeContext materialises:

identity
configuration
secrets
database configuration views
runtime paths
runtime metadata

Applications are expected to consume runtime resources (and SecretsApi) through RuntimeContext.

## Runtime Construction Flow

Runtime construction follows the sequence:

```text

Configuration Views
    ↓
SecretsApi Construction
    ↓
Path Materialisation
    ↓
Database View Extraction
    ↓
RuntimeContext
```

For example:

```python
context = build_runtime_context(
    identity=identity,
)
```
which currently materialises:
```text
configuration
secret services
database configuration views
runtime paths
runtime metadata
```

and returns a configured RuntimeContext.

## Runtime Discovery

`mxm-runtime` provides discovery utilities for determining runtime characteristics.

Examples:

```python
machine = discover_machine()
substrate = discover_substrate()
```

These functions derive MXM runtime selectors from operating-system facts.

The resulting values are suitable for configuration resolution and runtime construction.

## Relationship To mxm-config

`mxm-config` owns:

```text
configuration storage
configuration loading
configuration merging
configuration views
```

`mxm-runtime` consumes configuration and constructs runtime services from it.

mxm-runtime also extracts and materialises selected configuration views
required for runtime operation.

Examples:
```text
mxm_secrets
mxm_databases
mxm_paths
```

Example:

```text
RuntimeIdentity
    ↓
mxm-config
    ↓
MXMConfig
    ↓
RuntimeContext
```

## Relationship To mxm-secrets

`mxm-secrets` owns:

```text
secret references
authorization
resolution
retrieval
```

`mxm-runtime` constructs configured secret services and makes them available through RuntimeContext.

Applications are expected to consume:

```python
context.secrets
```

rather than constructing SecretsApi instances directly.

## Installation

```bash
pip install mxm-runtime
```

## Usage

Construct a RuntimeContext:

```python
from mxm.runtime import build_runtime_context

context = build_runtime_context(
    identity=identity,
)
```

Access configured services:

```python
api_key = context.secrets.get_secret(
    "databento_api_key",
    identity=context.identity,
)
```

```python
db_config = context.db_configs.operational_state

print(db_config.host)
print(db_config.name)

data_root = context.paths.data_root
```

## Design Principles

- **Explicit runtime identity**
  Runtime identity is always represented explicitly.

- **Configuration-driven construction**
  Runtime behaviour is determined through configuration rather than hardcoded wiring.

- **Separation of concerns**
  Discovery, configuration, resolution, construction, and application logic remain separate.

- **Strict typing**
  Fully Pyright-clean and PEP 561 compliant.

- **Minimal implicit behaviour**
  Runtime construction is deterministic and inspectable.

- **Composable services**
  Runtime services are assembled from independent packages.

## Development

```bash
poetry install

make check
```

Run the RuntimeContext smoke test:

```bash
poetry run python scripts/smoke_runtime_context.py
```

## Status

Current release status:

```text
Runtime Identity Discovery Complete
Configuration Integration Complete
Secrets Integration Complete
Runtime Path Materialisation Complete
Database View Materialisation Complete
Store Integration In Progress
```

Current RuntimeContext materialises:

```text
configuration
secrets
database configuration views
runtime paths
runtime metadata
```

Additional services will be added incrementally.

## License

MIT License. See [LICENSE](LICENSE).
