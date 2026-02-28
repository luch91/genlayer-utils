# Best Practices & Common Patterns

This document grew from [a community issue](https://github.com/genlayerlabs/genlayer-docs/issues/345)
and was originally published as a Gist. It has since been incorporated into **genlayer-utils**
as the canonical guide to writing reliable GenLayer contracts.

The guide is lengthy; the sections below mirror the original structure and point to
helper functions in this library whenever possible.

## Non-Deterministic Block Patterns

Every call to `gl.nondet.web` or `gl.nondet.exec_prompt` must happen inside a
function passed to an equivalence principle (`gl.eq_principle.strict_eq`,
`prompt_comparative`, or `prompt_non_comparative`). The most common pattern is:

```python
import json

def fetch_and_analyze(url, claim_text):
    def _inner():
        web_data = gl.nondet.web.render(url, mode="text")
        result = gl.nondet.exec_prompt(
            f"Fact-check this claim: {claim_text}\n\nEvidence: {web_data}\n\n"
            "Respond ONLY with JSON: {\"verdict\": \"<true|false>\"}",
            response_format="json",
        )
        return json.dumps(result, sort_keys=True)  # sort_keys is critical!

    raw = gl.eq_principle.strict_eq(_inner)
    return json.loads(raw)
```

See `nondet.py` for helpers such as `web_llm_strict` that encapsulate this boilerplate.

### Choosing an equivalence principle

| Principle                | Use When                                    |
|--------------------------|---------------------------------------------|
| `strict_eq`              | Output is constrained (yes/no, small JSON)  |
| `prompt_comparative`     | "Close enough" is acceptable               |
| `prompt_non_comparative` | Output is subjective/creative               |

Always prefer `strict_eq` for performance and determinism; fall back only when necessary.

## Prompt Engineering for Consensus

Prompts must narrow the output space to maximize validator agreement:

* Constrain outputs with enums (`<true|false>`) or fixed categories.
* Use `response_format="json"` and ask for valid JSON only.
* Short prompts with few fields reduce disagreement.
* Add explicit instructions such as "Respond ONLY with valid JSON, no extra text".

A few useful templates live in `llm.py` (e.g. `fact_check_prompt`, `classify_prompt`).

## Access Control Patterns

The platform has no built-in ACL, so contracts implement their own guards.

```python
def require_sender(expected):
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized: caller is not the expected address")

@gl.public.write
def admin_action(self) -> None:
    require_sender(self._owner)
    # ...
```

Other patterns include ownership transfer and role-based maps (guards are provided
in `access_control.py`).

## Storage Patterns

Common helpers are provided in `storage.py`:

* `increment_or_init` for counters
* `treemap_paginate` for paging large maps
* `address_map_to_dict` to convert address-keyed maps for JSON views

Example: paginating a `TreeMap` in a view method.

## Debugging Tips

1. Use GenLayer Studio for iteration.
2. Test storage/view logic before adding nondeterministic calls.
3. Mock web/AI results when starting.
4. If transactions fail repeatedly, your prompt is likely too unconstrained.
5. Prefer `mode="text"` for web.render() for consistency.

## Common Mistakes

| Mistake                                | Fix                                                                 |
|----------------------------------------|---------------------------------------------------------------------|
| Forgetting `sort_keys=True`             | Always `json.dumps(result, sort_keys=True)` before `strict_eq`      |
| Using `dict`/`list` for storage         | Use `TreeMap` / `DynArray` instead                                 |
| Missing `@allow_storage @dataclass`     | Required on every stored custom class                              |
| Calling `gl.nondet` outside equivalent  | Wrap in `gl.eq_principle.*` function                               |


> For the full original text, see the [gist](https://gist.github.com/luch91/d865f976ed04785890ca6cf84ef13cce).

```text
# end of document
```
