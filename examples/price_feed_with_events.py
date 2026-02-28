# {"Depends":"py-genlayer:test"}
# Price Feed with Events — Example GenLayer Intelligent Contract
# Uses: nondet, storage, access_control helpers from genlayer-utils
#

from genlayer import *

# helpers copied from genlayer-utils, to make this contract self‑contained

def require_sender(expected):
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized: caller is not the expected address")


def append_indexed_event(event_table: TreeMap, event_name: str, topics, blob):
    arr = event_table.get_or_insert_default(event_name)
    arr.append({"topics": topics, "blob": blob})


def query_indexed_events(event_table: TreeMap, event_name: str, offset: int = 0, limit: int = 100):
    if event_name not in event_table:
        return []
    arr = event_table[event_name]
    end = offset + limit
    try:
        return arr[offset:end]
    except Exception:
        items = []
        idx = 0
        for item in arr:
            if idx < offset:
                idx += 1
                continue
            if len(items) >= limit:
                break
            items.append(item)
            idx += 1
        return items


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
