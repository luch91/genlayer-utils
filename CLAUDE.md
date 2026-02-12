# CLAUDE.md

## Project Overview
genlayer-utils is a reusable patterns library for GenLayer Intelligent Contracts. It provides copy-pasteable helper functions for common contract patterns.

## Key Constraints
- GenVM runs contracts as single Python files — no pip imports at runtime
- Library code is meant to be copied into contracts, not imported as a package
- All code must be valid within the GenVM execution environment
- Contracts use `from genlayer import *` for SDK access

## GenLayer SDK Reference
- Full API: https://sdk.genlayer.com/main/_static/ai/api.txt
- Full docs: https://docs.genlayer.com/full-documentation.txt

## Module Structure
- `src/genlayer_utils/` — Library source code (5 modules)
- `examples/` — Complete deployable contracts using the library
- `docs/` — Documentation for each module
- `tests/` — Integration tests using gltest

## GenLayer Patterns
- Storage: `TreeMap[K, V]`, `DynArray[T]`, `@allow_storage @dataclass`
- Decorators: `@gl.public.view`, `@gl.public.write`, `@gl.public.write.payable`
- Non-deterministic: inner function + `gl.eq_principle.strict_eq(fn)`
- Web: `gl.nondet.web.render(url, mode="text")`, `gl.nondet.web.get(url)`
- LLM: `gl.nondet.exec_prompt(prompt, response_format="json")`
- Always `json.dumps(result, sort_keys=True)` for determinism in strict_eq
