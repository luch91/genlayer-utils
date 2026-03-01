# Changelog

## 0.1.0

- Add the initial `genlayer-utils` helper modules under `src/genlayer_utils/`:
  nondeterministic execution helpers, prompt templates, access control guards,
  storage helpers, and web-oracle helpers.
- Add example GenLayer contracts covering fact checking, price feeds, content
  moderation, voting, indexed events, gas-aware write workflows, and a minimal
  upgradeable proxy pattern.
- Add module docs plus a consolidated `docs/best-practices.md` guide for
  non-deterministic execution, prompt design, storage patterns, access control,
  indexed events, and upgrade/proxy patterns.
- Add unit-style tests using a fake GenLayer shim for helper modules and keep
  optional `gltest` integration tests for deployable examples.
- Add Python packaging metadata and a basic GitHub Actions CI workflow for the
  unit test layer.

