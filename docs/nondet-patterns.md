# Non-Deterministic Block Helpers

## The Problem

Every GenLayer contract that uses web access + LLM repeats the same 15-20 line pattern:

```python
def _do_something(self, url):
    def inner_function():
        web_data = gl.nondet.web.render(url, mode="text")
        prompt = f"Analyze this: {web_data}"
        result = gl.nondet.exec_prompt(prompt, response_format="json")
        return json.dumps(result, sort_keys=True)
    raw = gl.eq_principle.strict_eq(inner_function)
    return json.loads(raw)
```

This boilerplate is identical in structure across every contract. The only things that change are the URL, prompt, and how you use the result.

## The Solution

Three functions that wrap the entire pattern:

### `web_llm_strict(url, prompt_template)`

Fetch a web page, run an LLM prompt against it, and return the consensus result.

```python
# Before: 8 lines
def _check(self, url):
    def _inner():
        data = gl.nondet.web.render(url, mode="text")
        result = gl.nondet.exec_prompt(f"Analyze: {data}", response_format="json")
        return json.dumps(result, sort_keys=True)
    return json.loads(gl.eq_principle.strict_eq(_inner))

# After: 1 line
result = web_llm_strict(url=url, prompt_template="Analyze: {web_data}")
```

**Parameters:**
- `url` — URL to fetch
- `prompt_template` — Prompt with `{web_data}` placeholder
- `mode` — `"text"` (default), `"html"`, or `"screenshot"`
- `response_format` — `"json"` (default) or `"text"`

### `llm_strict(prompt)`

Run an LLM prompt without web fetching. For when you already have the data.

```python
result = llm_strict("Classify this text as positive or negative: 'Great product!'")
# result: {"sentiment": "positive", "confidence": "high"}
```

### `web_llm_comparative(url, prompt_template, principle)`

Like `web_llm_strict` but uses comparative equivalence instead of strict. Use when outputs may vary but should be semantically similar.

```python
summary = web_llm_comparative(
    url="https://example.com/article",
    prompt_template="Summarize: {web_data}",
    principle="Summaries are equivalent if they cover the same key points"
)
```

## When to Use Which

| Function | Equivalence | Best For |
|----------|-------------|----------|
| `web_llm_strict` | `strict_eq` | Facts, categories, structured JSON |
| `llm_strict` | `strict_eq` | Classification, yes/no, data already available |
| `web_llm_comparative` | `prompt_comparative` | Summaries, descriptions, free-form text |
