import json
import types
import sys
import os

# Ensure the repo root is on sys.path so `src` package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

# This test uses monkeypatch to simulate minimal parts of the `gl` API so that
# helpers in `src/genlayer_utils/nondet.py` can be exercised without GenVM.

def make_fake_gl(monkeypatch):
    fake = types.SimpleNamespace()

    class Web:
        @staticmethod
        def get(url, headers=None):
            return types.SimpleNamespace(status=200, body=b'ok', headers={})

        @staticmethod
        def render(url, mode='text', wait_after_loaded=None):
            return f"rendered:{url}"

    def exec_prompt(prompt, response_format='json'):
        if response_format == 'json':
            return {"ok": True}
        return "ok"

    fake.nondet = types.SimpleNamespace(web=Web(), exec_prompt=exec_prompt)

    class EP:
        @staticmethod
        def strict_eq(fn):
            # For testing, call the function and return its raw output
            return fn()

    fake.eq_principle = EP()

    # Patch into the modules that import `gl` as `from genlayer import *`
    # We'll inject `gl` into sys.modules references used by helpers by creating
    # a minimal genlayer and genlayer.gl module.
    gl_mod = types.SimpleNamespace(nondet=fake.nondet, eq_principle=fake.eq_principle)
    genlayer = types.SimpleNamespace(gl=gl_mod)

    monkeypatch.setitem(sys.modules, 'genlayer', genlayer)
    monkeypatch.setitem(sys.modules, 'genlayer.gl', gl_mod)
    return gl_mod


def test_exec_prompt_with_retry(monkeypatch):
    make_fake_gl(monkeypatch)
    from src.genlayer_utils import nondet

    res = nondet.exec_prompt_with_retry("test prompt", response_format="json", max_retries=2)
    # exec_prompt_with_retry may return a JSON string or a dict; normalize
    if isinstance(res, str):
        res = json.loads(res)
    assert isinstance(res, dict)
    assert res.get("ok") is True


def test_web_get_with_retry(monkeypatch):
    make_fake_gl(monkeypatch)
    from src.genlayer_utils import nondet

    resp = nondet.web_get_with_retry("https://example.com", max_retries=2)
    assert hasattr(resp, 'status')
    assert resp.status == 200


def test_record_event_strict(monkeypatch):
    # Simulate a simple TreeMap-like structure using dict
    make_fake_gl(monkeypatch)
    from src.genlayer_utils import nondet

    # Minimal TreeMap-like object: dict with get_or_insert_default
    class MockDynArray(list):
        def append(self, v):
            super().append(v)

    class MockTable(dict):
        def get_or_insert_default(self, key):
            if key not in self:
                self[key] = MockDynArray()
            return self[key]

    table = MockTable()
    # Use string topics here so the JSON serialization in the test environment succeeds
    record = nondet.record_event_strict(table, 'Ev', ('t1',), {'a': 1})
    assert isinstance(record, dict)
    assert table['Ev'][0]['blob'] == {'a': 1}
