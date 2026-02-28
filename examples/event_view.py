# { "Version": "v0.1.0", "Depends": "py-genlayer:test" }
# Event View — Example GenLayer Intelligent Contract
# Uses: storage, nondet helpers from genlayer-utils
#

from genlayer import *

class EventExample(gl.Contract):
    _events: TreeMap[str, DynArray[dict]]

    def __init__(self):
        # nothing else to init; DynArray will be created on demand
        pass

    @gl.public.write
    def emit_event(self, name: str, payload: str) -> None:
        # store in index
        append_indexed_event(self._events, name, (b"topic1",), payload)
        # also emit raw event for external listeners
        gl.advanced.emit_raw_event([name.encode('utf-8')], payload)

    @gl.public.view
    def get_events(self, name: str, offset: int = 0, limit: int = 100) -> list:
        return query_indexed_events(self._events, name, offset=offset, limit=limit)
