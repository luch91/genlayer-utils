import json

import pytest

from tests.support import fresh_import, install_fake_genlayer


def test_exec_prompt_with_retry_retries_then_succeeds(monkeypatch):
    attempts = {"count": 0}

    def exec_prompt(_prompt, response_format="json"):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("temporary failure")
        return {"ok": True} if response_format == "json" else "ok"

    install_fake_genlayer(monkeypatch, exec_prompt=exec_prompt)
    nondet = fresh_import("src.genlayer_utils.nondet")

    result = nondet.exec_prompt_with_retry("prompt", response_format="json", max_retries=3)

    if isinstance(result, str):
        result = json.loads(result)
    assert result == {"ok": True}
    assert attempts["count"] == 3


def test_exec_prompt_with_retry_raises_last_exception(monkeypatch):
    def exec_prompt(_prompt, response_format="json"):
        raise RuntimeError("still broken")

    install_fake_genlayer(monkeypatch, exec_prompt=exec_prompt)
    nondet = fresh_import("src.genlayer_utils.nondet")

    with pytest.raises(RuntimeError, match="still broken"):
        nondet.exec_prompt_with_retry("prompt", max_retries=2)


def test_web_render_with_retry_forwards_wait_after_loaded(monkeypatch):
    calls = []

    def web_render(url, mode="text", wait_after_loaded=None):
        calls.append((url, mode, wait_after_loaded))
        if len(calls) == 1:
            raise RuntimeError("retry once")
        return "rendered page"

    install_fake_genlayer(monkeypatch, web_render=web_render)
    nondet = fresh_import("src.genlayer_utils.nondet")

    result = nondet.web_render_with_retry(
        "https://example.com",
        mode="html",
        wait_after_loaded="1500",
        max_retries=2,
    )

    assert result == "rendered page"
    assert calls == [
        ("https://example.com", "html", "1500"),
        ("https://example.com", "html", "1500"),
    ]
