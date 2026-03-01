# PR Submission Guide for genlayer-docs

## Goal

Submit the `docs/best-practices.md` guide from `genlayer-utils` upstream to
[`genlayer-docs`](https://github.com/genlayerlabs/genlayer-docs) as a canonical
community-authored patterns page.

## Recommended Scope

Keep the upstream PR narrowly focused on documentation:

- add the best-practices guide
- link it from the docs navigation
- reference `genlayer-utils` as an implementation/examples companion repo

Do not bundle unrelated SDK or Studio feature requests into the same PR.

## Submission Steps

1. Fork `genlayer-docs` on GitHub.
2. Create a branch such as `add/best-practices-guide`.
3. Copy [docs/best-practices.md](docs/best-practices.md)
   into the appropriate docs location in your fork.
4. Add the page to the docs sidebar or index used by `genlayer-docs`.
5. Open a PR using the template below.

## PR Description Template

```markdown
## Summary
Add a best-practices guide for GenLayer contract development, based on the
community-maintained `genlayer-utils` patterns library.

## What this adds
- Non-deterministic execution patterns and equivalence-principle guidance
- Prompt design tips for validator consensus
- Storage patterns and helper recipes
- Access-control patterns
- Indexed event and proxy/upgrade patterns
- A gas-aware preview/write workflow pattern

## Why
The official docs currently cover many individual concepts, but there is still
value in a single patterns-oriented guide that connects those concepts into
practical contract-building workflows.

## Related issues
Closes #345

## Validation
- Backed by helper implementations in `genlayer-utils`
- Backed by example contracts in `genlayer-utils/examples/`
- Backed by unit-style helper tests in `genlayer-utils/tests/`
- Optional `gltest` integration remains available in a GenLayer environment

## Notes
This PR is documentation-only. It does not attempt to add SDK or Studio
features; those should remain tracked in separate issues.
```

## Suggested Follow-ups

- Link selected examples from `genlayer-utils` back into official docs pages.
- Keep the guide synced with SDK terminology changes such as
  `gl.get_contract_at()`.
- Add a small “patterns” section in official docs that points readers to both
  the guide and the examples repository.

## Validation Checklist

When you have a working environment, verify these before calling the PR ready:

1. Run the unit test layer with `pytest -q`.
2. Deploy and exercise at least the core examples:
   `examples/fact_checker.py`,
   `examples/price_feed.py`,
   `examples/price_feed_with_events.py`,
   `examples/upgrade_proxy.py`.
3. Manually confirm the copied docs page renders correctly inside
   `genlayer-docs`.
