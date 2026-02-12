# { "Depends": "py-genlayer:test" }
#
# Price Feed — Example GenLayer Intelligent Contract
# Uses: web_oracle, access_control helpers from genlayer-utils
#
# A contract that fetches and stores asset prices from web sources.
# Demonstrates how GenLayer contracts can act as decentralized price oracles.

import json
from dataclasses import dataclass
from genlayer import *


# ─── genlayer-utils: web_oracle ─────────────────────────────────────────────

def fetch_and_extract(url, extraction_prompt, *, mode="text"):
    def _inner():
        web_data = gl.nondet.web.render(url, mode=mode)
        prompt = extraction_prompt.format(web_data=web_data)
        result = gl.nondet.exec_prompt(prompt, response_format="json")
        if isinstance(result, dict):
            return json.dumps(result, sort_keys=True)
        return result
    return json.loads(gl.eq_principle.strict_eq(_inner))


def fetch_price(url, asset_name):
    prompt = f"""Extract the current price of {asset_name} from this web page.

WEB CONTENT:
{{web_data}}

Respond ONLY with this exact JSON format, nothing else:
{{"price": "<numeric value as string>", "currency": "<USD|EUR|GBP|etc>", "timestamp": "<if available, otherwise unknown>"}}

Rules:
- Extract only the most recent/current price
- Use the primary currency shown on the page
- Your response must be valid JSON only, no extra text"""
    return fetch_and_extract(url, prompt)


# ─── genlayer-utils: access_control ─────────────────────────────────────────

def require_sender(expected):
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized: caller is not the expected address")


# ─── Contract ───────────────────────────────────────────────────────────────

@allow_storage
@dataclass
class PriceRecord:
    asset: str
    price: str
    currency: str
    source_url: str
    updated_by: str


class PriceFeed(gl.Contract):
    prices: TreeMap[str, PriceRecord]
    _owner: Address

    def __init__(self):
        self._owner = gl.message.sender_address

    @gl.public.write
    def update_price(self, asset: str, source_url: str) -> None:
        """Fetch the current price of an asset from a web source."""
        result = fetch_price(source_url, asset)

        self.prices[asset] = PriceRecord(
            asset=asset,
            price=result["price"],
            currency=result.get("currency", "USD"),
            source_url=source_url,
            updated_by=gl.message.sender_address.as_hex,
        )

    @gl.public.view
    def get_price(self, asset: str) -> dict:
        """Get the latest stored price for an asset."""
        if asset not in self.prices:
            raise Exception(f"No price data for {asset}")
        p = self.prices[asset]
        return {
            "asset": p.asset,
            "price": p.price,
            "currency": p.currency,
            "source_url": p.source_url,
        }

    @gl.public.view
    def get_all_prices(self) -> list:
        """Get all stored prices."""
        return [
            {"asset": p.asset, "price": p.price, "currency": p.currency}
            for _, p in self.prices.items()
        ]

    @gl.public.write
    def remove_price(self, asset: str) -> None:
        """Remove a price entry (owner only)."""
        require_sender(self._owner)
        if asset in self.prices:
            del self.prices[asset]
