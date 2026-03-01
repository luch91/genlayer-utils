# {"Depends":"py-genlayer:test"}
# Price Feed Gas-aware Workflow — Example GenLayer Intelligent Contract
# Uses: storage helpers from genlayer-utils
#

from genlayer import *

# Gas-aware price feed pattern:
# 1) Frontend fetches/parses external data off-chain.
# 2) Frontend calls a pure view method to preview the normalized write payload.
# 3) Submit a minimal write that stores the final price (small, low-gas write).


class PriceFeedGasWorkflow(gl.Contract):
    _prices: TreeMap[str, u256]
    _owner: Address

    def __init__(self):
        self._owner = gl.message.sender_address

    @gl.public.view
    def preview_price_update(self, symbol: str, raw_price: str, decimals: u8 = 2) -> dict:
        """
        Normalize an off-chain fetched price into the exact on-chain write payload.

        This method is intentionally pure: the frontend performs the web/API fetch
        off-chain, then calls this view to confirm how the contract will encode the
        value before sending the write transaction.
        """
        normalized = int(float(raw_price) * (10 ** decimals))
        current = self._prices.get(symbol, 0)
        return {
            "symbol": symbol,
            "price": normalized,
            "previous_price": current,
            "changed": current != normalized,
        }

    @gl.public.write
    def update_price(self, symbol: str, price: u256) -> None:
        # Keep the write minimal to reduce gas: just store the value.
        if gl.message.sender_address != self._owner:
            raise Exception("Only owner")
        self._prices[symbol] = price

    @gl.public.view
    def get_price(self, symbol: str) -> u256:
        return self._prices.get(symbol, 0)
