# genlayer-utils: nondet.py
# Non-deterministic block helpers for GenLayer Intelligent Contracts
#
# These functions eliminate the 15-20 line boilerplate pattern that every
# contract using web access + LLM must repeat. Copy the functions you need
# into the top of your contract file.
#
# Requires: from genlayer import *
#           import json

import json
from genlayer import *


def web_llm_strict(
    url: str,
    prompt_template: str,
    *,
    mode: str = "text",
    response_format: str = "json",
) -> dict | str:
    """
    Fetch a web page, run an LLM prompt against it, and return the
    consensus result. Wraps the full non-deterministic block pattern.

    The prompt_template should contain a {web_data} placeholder that will
    be replaced with the fetched web content.

    Args:
        url: URL to fetch
        prompt_template: Prompt string with {web_data} placeholder
        mode: "text", "html", or "screenshot"
        response_format: "json" or "text"

    Returns:
        Parsed dict (if json) or str after strict_eq consensus

    Example:
        prompt = "Fact-check this claim using the evidence.\\n{web_data}"
        result = web_llm_strict(url="https://example.com", prompt_template=prompt)
        # result is a dict like {"verdict": "true", "explanation": "..."}
    """
    def _inner() -> str:
        web_data = gl.nondet.web.render(url, mode=mode)
        filled_prompt = prompt_template.format(web_data=web_data)
        result = gl.nondet.exec_prompt(
            filled_prompt, response_format=response_format
        )
        if isinstance(result, dict):
            return json.dumps(result, sort_keys=True)
        return result

    raw = gl.eq_principle.strict_eq(_inner)
    if response_format == "json":
        return json.loads(raw)
    return raw


def llm_strict(prompt: str, *, response_format: str = "json") -> dict | str:
    """
    Run an LLM prompt and get strict-equality consensus.
    No web fetch — for prompts that operate on data already available.

    Args:
        prompt: The full prompt to send to the LLM
        response_format: "json" or "text"

    Returns:
        Parsed dict (if json) or str after strict_eq consensus

    Example:
        result = llm_strict("Classify this text: 'I love this product'")
        # result is a dict like {"sentiment": "positive", "confidence": "high"}
    """
    def _inner() -> str:
        result = gl.nondet.exec_prompt(prompt, response_format=response_format)
        if isinstance(result, dict):
            return json.dumps(result, sort_keys=True)
        return result

    raw = gl.eq_principle.strict_eq(_inner)
    if response_format == "json":
        return json.loads(raw)
    return raw


def web_llm_comparative(
    url: str,
    prompt_template: str,
    principle: str,
    *,
    mode: str = "text",
) -> str:
    """
    Fetch a web page, run an LLM prompt, and validate with comparative
    equivalence. Use when outputs may vary but should be semantically similar.

    Args:
        url: URL to fetch
        prompt_template: Prompt string with {web_data} placeholder
        principle: How to compare outputs, e.g.
                   "Results are equivalent if ratings differ by less than 0.1"
        mode: "text", "html", or "screenshot"

    Returns:
        str result after comparative consensus

    Example:
        result = web_llm_comparative(
            url="https://example.com/article",
            prompt_template="Summarize this article:\\n{web_data}",
            principle="Summaries are equivalent if they cover the same key points"
        )
    """
    def _inner() -> str:
        web_data = gl.nondet.web.render(url, mode=mode)
        filled_prompt = prompt_template.format(web_data=web_data)
        return gl.nondet.exec_prompt(filled_prompt)

    return gl.eq_principle.prompt_comparative(_inner, principle)


def exec_prompt_with_retry(prompt: str, *, response_format: str = "json", max_retries: int = 3) -> dict | str:
    """
    Run `gl.nondet.exec_prompt` with simple retry logic for transient failures.

    Note: this is a thin helper that retries exceptions raised by the
    underlying call. It does not add timeouts (those are platform/SDK
    features) but it can improve robustness in the face of intermittent
    provider errors.

    Usage: call from inside an equivalence leader function.
    """
    attempt = 0
    last_exc = None
    while attempt < max_retries:
        try:
            result = gl.nondet.exec_prompt(prompt, response_format=response_format)
            if isinstance(result, dict):
                return json.dumps(result, sort_keys=True) if response_format == "json" else result
            return result
        except Exception as e:
            last_exc = e
            attempt += 1
            # No sleep available in GenVM; just retry immediately.
            continue
    # If we exhausted retries, re-raise the last exception to surface the error
    raise last_exc


def web_render_with_retry(url: str, *, mode: str = "text", max_retries: int = 3, wait_after_loaded: str | None = None) -> str:
    """
    Render a webpage with retries for transient renderer failures.

    Callers should use this inside their leader function when performing
    non-deterministic web fetches.
    """
    attempt = 0
    last_exc = None
    while attempt < max_retries:
        try:
            if wait_after_loaded is not None:
                return gl.nondet.web.render(url, mode=mode, wait_after_loaded=wait_after_loaded)
            return gl.nondet.web.render(url, mode=mode)
        except Exception as e:
            last_exc = e
            attempt += 1
            continue
    raise last_exc
