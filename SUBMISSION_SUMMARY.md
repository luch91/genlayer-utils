# genlayer-utils Submission Summary

## What It Is

`genlayer-utils` is a community-maintained patterns library for GenLayer
Intelligent Contracts. It packages common contract-building workflows into
copy-pasteable helpers, documentation, and example contracts.

## Problem It Solves

GenLayer contract authors repeatedly reimplement the same boilerplate for:

- non-deterministic web + LLM execution
- prompt construction for consensus-friendly outputs
- owner and role-based access control
- TreeMap / DynArray ergonomics
- web-oracle style extraction patterns
- indexed event storage and query workarounds

The official docs explain many of the primitives, but there is still a gap
between primitive APIs and practical patterns used in real contracts.

## What Has Been Delivered

- Helper modules under `src/genlayer_utils/`
- Example contracts under `examples/`
- Module docs under `docs/`
- A consolidated best-practices guide in `docs/best-practices.md`
- Unit-style helper tests under `tests/`
- Basic packaging and CI for the unit-test layer

## What It Does Not Claim To Solve

`genlayer-utils` is not a replacement for SDK or Studio features. It does not
add first-class support for:

- gas estimation
- event subscription/query APIs
- provider configuration bugs
- protocol-level upgradeability
- frontend/client type-system design

Instead, it offers practical patterns and interim workarounds where that is
appropriate, and it documents those boundaries explicitly.

## Why It Matters To The Ecosystem

- Improves developer onboarding with concrete examples
- Reduces repeated boilerplate across GenLayer contracts
- Helps standardize safer contract patterns
- Provides upstreamable documentation content
- Creates a foundation for future SDK-guided patterns

## Current Validation Status

- Unit-style tests are present for helper modules
- Optional `gltest` integration tests are present for example contracts
- Full end-to-end validation still depends on a working local GenLayer / Studio
  environment

## Requested Feedback

- Which patterns are most useful to prioritize for v1?
- Which parts should be upstreamed into official docs first?
- Which current workarounds should be replaced by first-class SDK support?
