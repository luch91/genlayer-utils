import json

import pytest

from tests.support import fresh_import, install_fake_genlayer


def load_web_oracle(monkeypatch, **kwargs):
    install_fake_genlayer(monkeypatch, **kwargs)
    return fresh_import("src.genlayer_utils.web_oracle")


def test_fetch_json_api_parses_response(monkeypatch):
    def web_get(_url, headers=None):
        body = json.dumps({"asset": "BTC", "price": 123}).encode()
        return type("Resp", (), {"status": 200, "body": body, "headers": headers or {}})()

    web_oracle = load_web_oracle(monkeypatch, web_get=web_get)

    assert web_oracle.fetch_json_api("https://example.com/api") == {
        "asset": "BTC",
        "price": 123,
    }


def test_fetch_json_api_raises_on_non_200(monkeypatch):
    def web_get(_url, headers=None):
        return type("Resp", (), {"status": 503, "body": b"{}", "headers": headers or {}})()

    web_oracle = load_web_oracle(monkeypatch, web_get=web_get)

    with pytest.raises(Exception, match="API returned status 503"):
        web_oracle.fetch_json_api("https://example.com/api")


def test_fetch_and_extract_formats_prompt_and_parses_json(monkeypatch):
    seen = {}

    def web_render(url, mode="text", wait_after_loaded=None):
        seen["render"] = (url, mode, wait_after_loaded)
        return "rendered page"

    def exec_prompt(prompt, response_format="json"):
        seen["prompt"] = (prompt, response_format)
        return {"score": "7"}

    web_oracle = load_web_oracle(
        monkeypatch,
        web_render=web_render,
        exec_prompt=exec_prompt,
    )

    result = web_oracle.fetch_and_extract(
        "https://example.com/page",
        "Extract score from {web_data}",
        mode="html",
    )

    assert result == {"score": "7"}
    assert seen["render"] == ("https://example.com/page", "html", None)
    assert seen["prompt"] == ("Extract score from rendered page", "json")


def test_fetch_price_uses_asset_specific_prompt(monkeypatch):
    seen = {}

    def web_render(_url, mode="text", wait_after_loaded=None):
        return "page"

    def exec_prompt(prompt, response_format="json"):
        seen["prompt"] = prompt
        return {"price": "67500.42", "currency": "USD", "timestamp": "unknown"}

    web_oracle = load_web_oracle(
        monkeypatch,
        web_render=web_render,
        exec_prompt=exec_prompt,
    )

    result = web_oracle.fetch_price("https://example.com/btc", "Bitcoin")

    assert result["price"] == "67500.42"
    assert "Bitcoin" in seen["prompt"]
    assert "page" in seen["prompt"]


def test_fetch_score_uses_team_specific_prompt(monkeypatch):
    seen = {}

    def web_render(_url, mode="text", wait_after_loaded=None):
        return "scoreboard"

    def exec_prompt(prompt, response_format="json"):
        seen["prompt"] = prompt
        return {"score": "2:1", "winner": 1, "status": "finished"}

    web_oracle = load_web_oracle(
        monkeypatch,
        web_render=web_render,
        exec_prompt=exec_prompt,
    )

    result = web_oracle.fetch_score("https://example.com/match", "Arsenal", "Chelsea")

    assert result == {"score": "2:1", "winner": 1, "status": "finished"}
    assert "Arsenal" in seen["prompt"]
    assert "Chelsea" in seen["prompt"]
    assert "scoreboard" in seen["prompt"]
