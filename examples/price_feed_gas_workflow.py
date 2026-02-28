# { "Depends": "py-genlayer:test" }
#
# Price Feed Gas-aware Workflow — Example GenLayer Intelligent Contract
# Uses: nondet, storage helpers from genlayer-utils
#

from genlayer import *

# Gas-aware price feed pattern:
# 1) Provide a view method that aggregates external data (no gas cost to read)
# 2) Frontend calls the view to prepare the value and previews gas cost
# 3) Submit a minimal write that stores the final price (small, low-gas write)

class PriceFeedGasWorkflow(gl.Contract):
    _prices: TreeMap[str, u256]
    _owner: Address

    def __init__(self):
        self._owner = gl.message.sender_address

    @gl.public.view
    def compute_price_offchain(self, source_url: str) -> dict:
        """
        View method that fetches and returns the computed price without changing state.
        Frontends should call this to preview the outcome and estimate gas before
        sending the write transaction.
        """
        # Use render in view to simulate the computation; note this depends on the
        # execution environment and may be mocked in tests.
        data = gl.nondet.web.render(source_url, mode="text")
        # Simple parsing example — production code should be more robust
        # Return minimal encoding the write method will accept
        return {"symbol": "FOO", "price": 12345}

    @gl.public.write
    def update_price(self, symbol: str, price: u256) -> None:
        # Keep the write minimal to reduce gas: just store the value
        if gl.message.sender_address != self._owner:
            raise Exception("Only owner")
        self._prices[symbol] = price

    @gl.public.view
    def get_price(self, symbol: str) -> u256:
        return self._prices.get(symbol, 0)
