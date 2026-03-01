# Test: Price Feed example contract
#
# Run with: gltest (GenLayer Studio must be running)
#
# These tests deploy the price_feed.py example and verify
# that prices can be fetched from web sources and stored on-chain.

import pytest

pytest.importorskip("gltest", exc_type=ImportError)

from gltest import get_contract_factory, default_account
from gltest.helpers import load_fixture
from gltest.assertions import tx_execution_succeeded


def deploy_contract():
    factory = get_contract_factory("PriceFeed", path="examples/price_feed.py")
    contract = factory.deploy()
    return contract


def test_update_price():
    """Test fetching and storing a price from a web source."""
    contract = load_fixture(deploy_contract)

    result = contract.update_price(
        args=[
            "Bitcoin",
            "https://www.coingecko.com/en/coins/bitcoin",
        ],
        wait_interval=10000,
        wait_retries=15,
    )
    assert tx_execution_succeeded(result)

    # Verify the price was stored
    price = contract.get_price(args=["Bitcoin"])
    assert price["asset"] == "Bitcoin"
    assert len(price["price"]) > 0
    assert price["currency"] in ["USD", "EUR", "GBP"]


def test_get_all_prices():
    """Test listing all stored prices."""
    contract = load_fixture(deploy_contract)

    contract.update_price(
        args=["Bitcoin", "https://www.coingecko.com/en/coins/bitcoin"],
        wait_interval=10000,
        wait_retries=15,
    )

    prices = contract.get_all_prices(args=[])
    assert len(prices) >= 1


def test_owner_remove():
    """Test that the owner can remove price entries."""
    contract = load_fixture(deploy_contract)

    contract.update_price(
        args=["Bitcoin", "https://www.coingecko.com/en/coins/bitcoin"],
        wait_interval=10000,
        wait_retries=15,
    )

    result = contract.remove_price(args=["Bitcoin"])
    assert tx_execution_succeeded(result)
