# Upstream genlayer-docs PR Package

Use this when opening the upstream PR against `genlayerlabs/genlayer-docs`.

## Suggested PR Title

`docs: add best practices and common patterns guide`

## Suggested Branch Name

`add/best-practices-guide`

## PR Body

```md
## Summary
Add a best-practices guide for GenLayer contract development, based on the
community-maintained `genlayer-utils` patterns library.

## What this adds
- Non-deterministic execution patterns and equivalence-principle guidance
- Prompt design tips for validator consensus
- Storage patterns and helper recipes
- Access-control patterns
- Indexed event patterns
- A minimal proxy/upgrade pattern
- A gas-aware preview/write workflow pattern

## Why
The official docs cover many individual primitives, but there is still value in
a single patterns-oriented guide that connects those concepts into practical
contract-building workflows and common implementation mistakes.

## Related issues
Closes #345

## Validation
- Backed by helper implementations in `genlayer-utils`
- Backed by example contracts in `genlayer-utils/examples/`
- Backed by unit-style helper tests in `genlayer-utils/tests/`
- Current helper-layer validation result: `21 passed, 2 skipped`
- Optional `gltest` integration remains environment-dependent

## Notes
This PR is documentation-only. It does not attempt to add SDK or Studio
features; those should remain tracked in separate issues.
```

## Copy Checklist

Before opening the PR, make sure you have done all of the following in your
`genlayer-docs` fork:

1. Copy [docs/best-practices.md](docs/best-practices.md) into the docs repo.
2. Add the new page to the docs sidebar/navigation.
3. Confirm internal links and headings render correctly.
4. Keep the PR scoped to documentation only.

## Reviewer Notes

If maintainers ask why this belongs upstream:

- it addresses the long-standing request for a common patterns guide
- it complements existing primitive/API pages rather than replacing them
- the implementation details live in `genlayer-utils`, while the conceptual
  guidance is appropriate for official docs
