# PR Submission Guide for genlayer-docs

## Next Steps

To submit the best-practices guide to the upstream [genlayer-docs](https://github.com/genlayerlabs/genlayer-docs) repository:

### Option 1: Use GitHub UI (Recommended)

1. **Fork genlayer-docs** on GitHub (if you haven't already)
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/<your-username>/genlayer-docs.git
   cd genlayer-docs
   ```

3. **Create a new branch**:
   ```bash
   git checkout -b add/best-practices-guide
   ```

4. **Copy the best-practices content**:
   - Copy `docs/best-practices.md` from genlayer-utils into `docs/best-practices.md` in your genlayer-docs fork
   - Update the `sidebars.js` or document index to include the new page

5. **Commit and push**:
   ```bash
   git add docs/best-practices.md
   git commit -m "docs: add best practices and common patterns guide

   - Migrated from genlayer-utils community guide
   - Covers non-deterministic patterns, prompt engineering, storage, access control
   - Includes event indexing and proxy upgrade patterns
   - References genlayer-utils library for copy-paste helpers"
   git push origin add/best-practices-guide
   ```

6. **Open a PR on GitHub**:
   - Go to https://github.com/genlayerlabs/genlayer-docs
   - Click "Compare & pull request"
   - Fill in the PR description (see template below)

### PR Description Template

```markdown
## Summary
Add a canonical best practices guide for GenLayer contract development, migrated from the genlayer-utils library.

## What's included
- Non-deterministic block patterns and equivalence principles
- Prompt engineering strategies for consensus
- Storage patterns (pagination, indexed events)
- Access control guards
- Upgrade/proxy forwarding patterns
- Gas-aware workflow patterns

## Related issues
Closes #345 (community request for patterns guide)

## Testing
This guide is backed by:
- genlayer-utils library helpers (in `src/genlayer_utils/`)
- Example contracts (in `examples/`)
- Mock-based tests run via CI (in `tests/`)

## Migration notes
- Content was originally published as a [community gist](https://gist.github.com/rasca/...)
- Now maintained as part of the genlayer-utils library
- Can be kept in sync with future library updates via cross-referencing

## Related PRs / Follow-ups
- Consider linking genlayer-docs to genlayer-utils for pattern examples
- Consider adding links back from genlayer-utils examples to the docs
```

---

## For GenVM Integration Tests

Once you have GenVM running locally, test the examples from genlayer-utils:

1. **Price Feed Example** (with events):
   ```bash
   deploy examples/price_feed_with_events.py
   ```

2. **Event Viewer Example**:
   ```bash
   deploy examples/event_view.py
   ```

3. **Upgrade Proxy Example**:
   ```bash
   deploy examples/upgrade_proxy.py
   ```

4. **Fact Checker Example**:
   ```bash
   deploy examples/fact_checker.py
   ```

These contracts exercise:
- Web + LLM strict_eq patterns
- Event indexing and querying
- Proxy forwarding for upgrades

---

## Status

- ✅ genlayer-utils repo: Pattern helpers implemented and tested locally
- ✅ Mock-based unit tests: Pass locally with pytest
- ✅ CI workflow: Added (.github/workflows/ci.yml)
- ⏳ genlayer-docs PR: Ready for submission (awaiting manual PR creation)
- ⏳ Issue #345 closure: Prepared (awaiting post)
- ⏳ GenVM integration: Example contracts ready to deploy (awaits GenVM environment)
