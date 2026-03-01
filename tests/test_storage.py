from tests.support import FakeAddress, fresh_import, install_fake_genlayer


class MockDynArray(list):
    pass


class MockTreeMap(dict):
    def get_or_insert_default(self, key):
        if key not in self:
            self[key] = MockDynArray()
        return self[key]


def load_storage(monkeypatch):
    install_fake_genlayer(monkeypatch)
    return fresh_import("src.genlayer_utils.storage")


def test_treemap_paginate_respects_offset_and_limit(monkeypatch):
    storage = load_storage(monkeypatch)

    items = MockTreeMap({"a": 1, "b": 2, "c": 3})

    assert storage.treemap_paginate(items, offset=1, limit=1) == [("b", 2)]


def test_increment_or_init_updates_existing_and_missing_keys(monkeypatch):
    storage = load_storage(monkeypatch)

    counters = MockTreeMap()
    storage.increment_or_init(counters, "votes")
    storage.increment_or_init(counters, "votes", amount=4)

    assert counters["votes"] == 5


def test_address_map_to_dict_serializes_address_keys(monkeypatch):
    storage = load_storage(monkeypatch)

    addresses = MockTreeMap(
        {
            FakeAddress("0x" + "1" * 40): 7,
            FakeAddress("0x" + "2" * 40): 3,
        }
    )

    assert storage.address_map_to_dict(addresses) == {
        "0x" + "1" * 40: 7,
        "0x" + "2" * 40: 3,
    }


def test_query_indexed_events_supports_slice_and_fallback(monkeypatch):
    storage = load_storage(monkeypatch)

    event_table = MockTreeMap()
    storage.append_indexed_event(event_table, "PriceUpdated", (b"BTC",), {"price": 1})
    storage.append_indexed_event(event_table, "PriceUpdated", (b"ETH",), {"price": 2})

    assert storage.query_indexed_events(event_table, "PriceUpdated", offset=1, limit=1) == [
        {"topics": (b"ETH",), "blob": {"price": 2}}
    ]

    class NonSliceableDynArray(MockDynArray):
        def __getitem__(self, item):
            if isinstance(item, slice):
                raise TypeError("no slices")
            return super().__getitem__(item)

    fallback_table = MockTreeMap({"PriceUpdated": NonSliceableDynArray(event_table["PriceUpdated"])})

    assert storage.query_indexed_events(fallback_table, "PriceUpdated", offset=0, limit=2) == [
        {"topics": (b"BTC",), "blob": {"price": 1}},
        {"topics": (b"ETH",), "blob": {"price": 2}},
    ]
