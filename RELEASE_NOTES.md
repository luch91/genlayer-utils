# Release Notes — 0.1.0

`genlayer-utils` is an initial community patterns library for GenLayer
Intelligent Contracts. The release focuses on reusable copy-paste helpers,
example contracts, and documentation that close common developer-experience
gaps while first-class SDK patterns are still maturing.

Included in this release:

- Helper modules for nondeterministic execution, LLM prompt templates, access
  control, storage ergonomics, and web-oracle patterns.
- Example contracts demonstrating practical contract patterns, including
  fact-checking, price feeds, indexed events, a gas-aware preview/write
  workflow, and proxy forwarding.
- A consolidated best-practices guide intended to support upstream docs work.
- Mock-based unit tests and a basic CI workflow for the helper library.

Validation status:

- Unit tests are present in the repository and are intended to run with `pytest`.
- `gltest` integration tests remain optional and require a working GenLayer
  environment / Studio instance.

See [CHANGELOG.md](CHANGELOG.md) for the detailed change summary.
