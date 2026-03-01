import types

import pytest

from tests.support import FakeAddress, fresh_import, install_fake_genlayer


def load_access_control(monkeypatch, **kwargs):
    install_fake_genlayer(monkeypatch, **kwargs)
    return fresh_import("src.genlayer_utils.access_control")


def test_require_sender_allows_expected_sender(monkeypatch):
    access_control = load_access_control(monkeypatch, sender="0x" + "1" * 40)

    access_control.require_sender(FakeAddress("0x" + "1" * 40))


def test_require_sender_rejects_unexpected_sender(monkeypatch):
    access_control = load_access_control(monkeypatch, sender="0x" + "1" * 40)

    with pytest.raises(Exception, match="Unauthorized"):
        access_control.require_sender(FakeAddress("0x" + "2" * 40))


def test_require_value_enforces_minimum(monkeypatch):
    access_control = load_access_control(monkeypatch, value=5)

    access_control.require_value(5)

    with pytest.raises(Exception, match="Insufficient value"):
        access_control.require_value(6)


def test_require_not_zero_rejects_zero_address(monkeypatch):
    access_control = load_access_control(monkeypatch)

    with pytest.raises(Exception, match="Zero address not allowed"):
        access_control.require_not_zero(FakeAddress("0x" + "0" * 40))


def test_forward_to_impl_calls_method_with_value(monkeypatch):
    forwarded = {}

    class Target:
        def update_price(self, symbol, price):
            forwarded["args"] = (symbol, price)
            return "ok"

    class Impl:
        def emit(self, *, value):
            forwarded["value"] = value
            return Target()

    def get_contract_at(_impl_address):
        return Impl()

    access_control = load_access_control(
        monkeypatch,
        value=42,
        get_contract_at=get_contract_at,
    )

    result = access_control.forward_to_impl(
        FakeAddress("0x" + "3" * 40),
        "update_price",
        "BTC",
        123,
    )

    assert result == "ok"
    assert forwarded == {"value": 42, "args": ("BTC", 123)}


def test_forward_to_impl_rejects_unknown_method(monkeypatch):
    class Impl:
        def emit(self, *, value):
            return types.SimpleNamespace()

    def get_contract_at(_impl_address):
        return Impl()

    access_control = load_access_control(monkeypatch, get_contract_at=get_contract_at)

    with pytest.raises(Exception, match="Unknown method on implementation"):
        access_control.forward_to_impl(FakeAddress("0x" + "4" * 40), "missing_method")
