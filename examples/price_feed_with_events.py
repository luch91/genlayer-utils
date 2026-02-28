# { "Depends": "py-genlayer:test" }
#
# Price Feed with Events — Example GenLayer Intelligent Contract
# Uses: nondet, storage, access_control helpers from genlayer-utils
#

from genlayer import *

class PriceFeedWithEvents(gl.Contract):
    _prices: TreeMap[str, u256]
    _events: TreeMap[str, DynArray[dict]]

    def __init__(self):
        pass

    @gl.public.write
    def update_price(self, symbol: str, price: u256) -> None:
        require_sender(self._owner) if hasattr(self, '_owner') else None
        self._prices[symbol] = price
        append_indexed_event(self._events, 'PriceUpdated', (symbol.encode('utf-8'),), {'symbol': symbol, 'price': price})
        gl.advanced.emit_raw_event([b'PriceUpdated', symbol.encode('utf-8')], {'symbol': symbol, 'price': price})

    @gl.public.view
    def get_price(self, symbol: str) -> u256:
        return self._prices.get(symbol, 0)

    @gl.public.view
    def get_price_events(self, offset: int = 0, limit: int = 100) -> list:
        return query_indexed_events(self._events, 'PriceUpdated', offset=offset, limit=limit)
