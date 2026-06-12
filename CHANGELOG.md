# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

- _Nothing yet._

### Changed

- _Nothing yet._

### Deprecated

- _Nothing yet._

### Removed

- _Nothing yet._

### Fixed

- _Nothing yet._
## [0.1.1] - 2026-06-12

### Changed

- Relaxed shared CLI dependency constraints to improve compatibility across
  the MXM package ecosystem.
- Updated `rich` dependency range to allow newer compatible releases.
- Updated `typer` dependency range to allow newer compatible releases.
- Aligned `mxm-runtime` dependency policy with the versions already adopted by
  other MXM infrastructure packages such as `mxm-refdata`.

### Notes

This release contains no functional runtime changes.

The purpose of the release is to remove unnecessary dependency conflicts when
integrating `mxm-runtime` into downstream applications such as
`mxm-moneymachine` and to establish a more permissive compatibility policy for
shared CLI dependencies.
## [0.1.0] - 2026-06-12

### Added

- Added `RuntimeIdentity` discovery support:
  - machine discovery
  - substrate discovery
- Added `RuntimeContext` model.
- Added `RuntimePaths` model.
- Added `RuntimeMetadata` model.
- Added `build_runtime_context(...)` runtime constructor.
- Added RuntimeContext smoke-test script.
- Added comprehensive test coverage for:
  - runtime discovery
  - RuntimeContext construction
  - configuration integration
  - secrets integration

### Architecture

`mxm-runtime` establishes the runtime construction layer of the MXM architecture.

The package is responsible for:

```text
runtime discovery
configuration consumption
service construction
context assembly
```

and provides a single runtime entry point:

```python
context = build_runtime_context(
    identity=identity,
)
```

The resulting RuntimeContext represents the operational environment available
to MXM applications.

### Runtime Construction

Runtime construction now follows the sequence:

```text
RuntimeIdentity
    ↓
mxm-config
    ↓
Configuration Views
    ↓
Service Construction
    ↓
RuntimeContext
```

This separates:

```text
configuration ownership
```

from:

```text
runtime construction
```

and:

```text
application logic
```

### Integration

Added integration with:

```text
mxm-config
```

for configuration loading and configuration views.

Added integration with:

```text
mxm-secrets
```

for construction of configured SecretsApi instances from runtime configuration.

RuntimeContext currently materialises:

```text
identity
configuration
secrets
```

### Discovery Model

Introduced machine and substrate discovery.

Machine values represent MXM machine selectors used for machine-specific
configuration resolution rather than unique hardware identifiers.

Examples:

```text
bridge
monolith
wildling
```

Substrate values represent execution environments such as:

```text
local-process
docker
```

### Design

The runtime architecture is organised around:

```text
Authority
    ↓
Resolution
    ↓
Construction
    ↓
Application
```

with responsibilities separated across:

```text
mxm-config
mxm-secrets
mxm-runtime
```

### Compatibility

No breaking changes.

This is the initial public release of `mxm-runtime`.

### Status

Current RuntimeContext capabilities:

```text
identity
configuration
secrets
```

Future releases are expected to add:

```text
paths
databases
reference data services
storage services
execution services
```

while preserving the RuntimeContext construction model.

## Versions

[0.1.1]: https://github.com/moneyexmachina/mxm-runtime/releases/tag/v0.1.1
[0.1.0]: https://github.com/moneyexmachina/mxm-runtime/releases/tag/v0.1.0
