# genlayer-utils

Reusable patterns for GenLayer Intelligent Contracts.

**The first utility library for the GenLayer ecosystem.** Drop-in helper functions for the patterns every contract developer writes from scratch: non-deterministic blocks, LLM prompts, access control, web data extraction, and storage operations.

---

## Why?

Every GenLayer contract that uses web access + AI repeats the same 15-20 lines of boilerplate. There are zero reusable libraries in the ecosystem. This project fixes that.

### Before genlayer-utils (20 lines)

```python
def _fact_check(self, claim_text, source_url):
    def check_claim():
        web_data = gl.nondet.web.render(source_url, mode="text")
        prompt = f"""You are a fact-checker. Based on the evidence,
        determine whether this claim is true or false.
        CLAIM: {claim_text}
        EVIDENCE: {web_data}
        Respond ONLY with JSON: {{"verdict": "<true|false>", "explanation": "..."}}"""
        result = gl.nondet.exec_prompt(prompt, response_format="json")
        return json.dumps(result, sort_keys=True)
    raw = gl.eq_principle.strict_eq(check_claim)
    return json.loads(raw)
```

### After genlayer-utils (3 lines)

```python
prompt = fact_check_prompt(claim_text, "{web_data}")
result = web_llm_strict(url=source_url, prompt_template=prompt)
# result: {"verdict": "true", "explanation": "..."}
```

---

## Modules

| Module | What it does | Key functions |
|--------|-------------|---------------|
| **[nondet](docs/nondet-patterns.md)** | Non-deterministic block helpers | `web_llm_strict()`, `llm_strict()`, `web_llm_comparative()` |
| **[llm](docs/llm-templates.md)** | LLM prompt templates & validators | `classify_prompt()`, `fact_check_prompt()`, `extract_prompt()`, `yes_no_prompt()` |
| **[access_control](docs/access-control.md)** | Owner & role-based guards | `require_sender()`, `require_value()`, Ownable pattern, Role-based pattern |
| **[web_oracle](docs/web-oracle.md)** | Web data extraction with consensus | `fetch_json_api()`, `fetch_price()`, `fetch_score()`, `fetch_and_extract()` |
| **[storage](docs/storage-helpers.md)** | TreeMap/DynArray utilities | `increment_or_init()`, `treemap_paginate()`, `address_map_to_dict()` |

---

## How to Use

GenLayer contracts are deployed as single Python files. You **copy the functions you need** directly into your contract.

```python
# { "Depends": "py-genlayer:test" }
import json
from genlayer import *

# ─── Paste from genlayer-utils ──────────────────────────────
def web_llm_strict(url, prompt_template, *, mode="text", response_format="json"):
    def _inner():
        web_data = gl.nondet.web.render(url, mode=mode)
        result = gl.nondet.exec_prompt(
            prompt_template.format(web_data=web_data), response_format=response_format
        )
        return json.dumps(result, sort_keys=True) if isinstance(result, dict) else result
    raw = gl.eq_principle.strict_eq(_inner)
    return json.loads(raw) if response_format == "json" else raw

def require_sender(expected):
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized")

# ─── Your contract ──────────────────────────────────────────
class MyContract(gl.Contract):
    ...
```

See [Getting Started](docs/getting-started.md) for the full guide.

---

## Example Contracts

Complete, deployable contracts that demonstrate each module:

| Contract | Uses | Description |
|----------|------|-------------|
| [fact_checker.py](examples/fact_checker.py) | nondet, llm, access_control, storage | AI fact-checking dApp |
| [price_feed.py](examples/price_feed.py) | web_oracle, access_control | Decentralized price oracle |
| [content_moderator.py](examples/content_moderator.py) | nondet, llm, storage | AI content classification |
| [voting.py](examples/voting.py) | access_control, storage | On-chain voting with roles |

---

## What Each Module Saves You

| Pattern | Without genlayer-utils | With genlayer-utils |
|---------|----------------------|---------------------|
| Web + LLM + consensus | 15-20 lines | 1-2 lines |
| Prompt engineering | Manual, error-prone | Pre-built templates |
| Owner-only methods | 3-4 lines per method | 1 line: `require_sender(self._owner)` |
| Increment counter | 3 lines | 1 line: `increment_or_init(data, key)` |
| Paginate TreeMap | 8-10 lines | 1 line: `treemap_paginate(data, offset, limit)` |
| Fetch API data | 10-15 lines | 1 line: `fetch_json_api(url)` |
| Extract web data | 15-20 lines | 1 line: `fetch_price(url, "Bitcoin")` |

---

## Project Structure

```
genlayer-utils/
  src/genlayer_utils/        # Library source (5 modules)
    nondet.py                # Non-deterministic block helpers
    llm.py                   # LLM prompt templates & validators
    access_control.py        # Owner & role-based access guards
    web_oracle.py            # Web data extraction with consensus
    storage.py               # TreeMap/DynArray helpers
  examples/                  # 4 complete, deployable contracts
  docs/                      # Documentation for each module
  tests/                     # Integration tests (gltest)
```

---

## Testing

Tests use the [gltest](https://docs.genlayer.com/developers/decentralized-applications/testing) framework. GenLayer Studio must be running.

```bash
# Select network
genlayer network

# Run tests
gltest
```

---

## Contributing

Contributions welcome! If you have a pattern you use repeatedly in your GenLayer contracts, it probably belongs here.

1. Fork the repo
2. Add your pattern to the appropriate module (or create a new one)
3. Add an example showing it in action
4. Add docs explaining when and why to use it
5. Submit a PR

---

## Resources

| Resource | URL |
|----------|-----|
| GenLayer Docs | [docs.genlayer.com](https://docs.genlayer.com) |
| SDK API Reference | [sdk.genlayer.com](https://sdk.genlayer.com/main/_static/ai/api.txt) |
| GenLayer Studio | [studio.genlayer.com](https://studio.genlayer.com) |
| genlayer-js SDK | [docs.genlayer.com/api-references/genlayer-js](https://docs.genlayer.com/api-references/genlayer-js) |

---

## License

MIT
