# LLM Prompt Templates

## The Problem

Writing prompts that work reliably with `strict_eq` consensus is tricky. Validators need to independently produce the same output, which means:
- Output must be constrained (not free-form)
- JSON format must be explicit
- Labels must be from a fixed set

Getting this wrong means validators disagree and transactions fail.

## Prompt Templates

### `classify_prompt(text, categories, context="")`

Classify text into one of the given categories.

```python
prompt = classify_prompt(
    text="This product is terrible, total waste of money",
    categories=["positive", "negative", "neutral"],
    context="You are analyzing customer reviews."
)
result = llm_strict(prompt)
# result: {"category": "negative", "confidence": "high", "reason": "..."}
```

### `extract_prompt(text, fields)`

Extract structured fields from unstructured text.

```python
prompt = extract_prompt(
    text="John Smith, age 32, works at Google as a software engineer in NYC",
    fields={
        "name": "person's full name",
        "age": "numeric age",
        "company": "employer name",
        "role": "job title",
    }
)
result = llm_strict(prompt)
# result: {"name": "John Smith", "age": "32", "company": "Google", "role": "software engineer"}
```

### `fact_check_prompt(claim, evidence, verdicts=None)`

Fact-check a claim against provided evidence. Designed to work with `web_llm_strict()` where evidence is a `{web_data}` placeholder.

```python
prompt = fact_check_prompt(
    claim="Python was created by Guido van Rossum in 1991",
    evidence="{web_data}",
)
result = web_llm_strict(
    url="https://en.wikipedia.org/wiki/Python_(programming_language)",
    prompt_template=prompt
)
# result: {"verdict": "true", "explanation": "Python was indeed created by..."}
```

Custom verdicts:
```python
prompt = fact_check_prompt(
    claim="The Earth is flat",
    evidence="{web_data}",
    verdicts=["true", "false", "misleading", "unverifiable"]
)
```

### `yes_no_prompt(question, context="")`

Binary yes/no questions. Maximum consensus reliability due to minimal output space.

```python
prompt = yes_no_prompt(
    question="Is this website a legitimate news source?",
    context="The website is cnn.com, a major US news network."
)
result = llm_strict(prompt)
# result: {"answer": "yes", "reason": "CNN is a well-established news network"}
```

## Response Validators

### `validate_json_fields(result, required_fields)`

```python
result = llm_strict(prompt)
if not validate_json_fields(result, ["verdict", "explanation"]):
    raise Exception("LLM response missing required fields")
```

### `validate_enum_field(result, field, allowed)`

```python
if not validate_enum_field(result, "verdict", ["true", "false", "partially_true"]):
    raise Exception(f"Invalid verdict: {result.get('verdict')}")
```

## Tips for Reliable Consensus

1. **Constrain the output** — `"<true|false>"` beats free-form text
2. **Use JSON format** — Always pass `response_format="json"`
3. **Sort keys** — The helpers do this automatically via `json.dumps(sort_keys=True)`
4. **Be explicit** — "Respond ONLY with JSON, no extra text"
5. **Fewer fields = higher agreement** — The smaller the output, the easier consensus
