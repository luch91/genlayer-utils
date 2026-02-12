# Getting Started with genlayer-utils

## What is genlayer-utils?

A collection of reusable patterns for GenLayer Intelligent Contracts. It provides helper functions for the most common tasks: non-deterministic blocks, LLM prompts, access control, web data extraction, and storage operations.

## How to Use

Since GenLayer contracts are deployed as single Python files, you **copy the functions you need** directly into your contract. Each module is designed so you can grab individual functions without pulling in the entire library.

### Step 1: Pick the functions you need

Browse the modules:
- [nondet](nondet-patterns.md) — Web + LLM + consensus in one call
- [llm](llm-templates.md) — Pre-built prompt templates
- [access_control](access-control.md) — Owner & role guards
- [web_oracle](web-oracle.md) — Web data extraction
- [storage](storage-helpers.md) — TreeMap/DynArray utilities

### Step 2: Copy them into your contract

Paste the functions at the top of your contract file, after your imports:

```python
# { "Depends": "py-genlayer:test" }
import json
from dataclasses import dataclass
from genlayer import *

# ─── genlayer-utils: nondet ─────────────────────────────────
def web_llm_strict(url, prompt_template, *, mode="text", response_format="json"):
    # ... (paste from src/genlayer_utils/nondet.py)

# ─── genlayer-utils: llm ────────────────────────────────────
def fact_check_prompt(claim, evidence, verdicts=None):
    # ... (paste from src/genlayer_utils/llm.py)

# ─── Your contract ──────────────────────────────────────────
class MyContract(gl.Contract):
    ...
```

### Step 3: Use them in your contract methods

```python
@gl.public.write
def resolve(self, claim_id: str) -> None:
    claim = self.claims[claim_id]
    prompt = fact_check_prompt(claim.text, "{web_data}")
    result = web_llm_strict(url=claim.source_url, prompt_template=prompt)
    claim.verdict = result["verdict"]
```

## Example Contracts

See the `examples/` directory for complete, deployable contracts:

| Contract | Modules Used | Description |
|----------|-------------|-------------|
| [fact_checker.py](../examples/fact_checker.py) | nondet, llm, access_control, storage | AI fact-checking |
| [price_feed.py](../examples/price_feed.py) | web_oracle, access_control | Asset price oracle |
| [content_moderator.py](../examples/content_moderator.py) | nondet, llm, storage | AI content classification |
| [voting.py](../examples/voting.py) | access_control, storage | On-chain voting |

## Why Copy-Paste?

GenLayer contracts run inside GenVM as standalone Python files. There's no mechanism to import third-party packages at runtime (like `pip install`). Copy-paste is how all contract libraries start — even OpenZeppelin began this way.

The benefit: zero dependencies, full transparency, and you only include what you use.
