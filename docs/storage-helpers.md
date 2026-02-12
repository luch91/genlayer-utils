# Storage Helpers

## The Problem

GenLayer uses `TreeMap` and `DynArray` instead of Python's `dict` and `list`. While powerful, they lack some convenience methods and developers write the same utility code repeatedly.

## Functions

### `increment_or_init(data, key, amount=1)`

Increment a value in a TreeMap, initializing to 0 if absent. Replaces the common 3-line pattern.

```python
# Before
if sender not in self.reputation:
    self.reputation[sender] = 0
self.reputation[sender] += 10

# After
increment_or_init(self.reputation, sender, 10)
```

### `treemap_paginate(data, offset=0, limit=10)`

Return a slice of a TreeMap as a list of `(key, value)` tuples.

```python
@gl.public.view
def get_claims_page(self, page: int) -> list:
    entries = treemap_paginate(self.claims, offset=page * 10, limit=10)
    return [{"id": k, "text": v.text} for k, v in entries]
```

### `treemap_to_list(data)`

Convert an entire TreeMap to a list of `(key, value)` tuples.

```python
@gl.public.view
def get_all(self) -> list:
    return treemap_to_list(self.entries)
```

### `treemap_to_dict(data, key_transform=None)`

Convert a TreeMap to a plain Python dict. Optionally transform keys.

```python
# Plain conversion
d = treemap_to_dict(self.scores)

# With key transformation
d = treemap_to_dict(self.data, key_transform=lambda addr: addr.as_hex)
```

### `address_map_to_dict(data)`

Convenience wrapper for `TreeMap[Address, V]` — converts Address keys to hex strings.

```python
@gl.public.view
def get_reputation(self) -> dict:
    return address_map_to_dict(self.reputation)
    # Returns: {"0xAbC...": 42, "0xDeF...": 17}
```

### `treemap_count(data)`

Count entries in a TreeMap (since `len()` isn't available).

```python
@gl.public.view
def total_claims(self) -> int:
    return treemap_count(self.claims)
```

## Common Storage Patterns

### Auto-incrementing IDs

```python
class MyContract(gl.Contract):
    _counter: u256

    def __init__(self):
        self._counter = 0

    def _next_id(self, prefix: str = "item") -> str:
        self._counter += 1
        return f"{prefix}_{self._counter}"
```

### Tracking unique entries per address

```python
class MyContract(gl.Contract):
    user_items: TreeMap[Address, DynArray[str]]

    @gl.public.write
    def add_item(self, item: str) -> None:
        items = self.user_items.get_or_insert_default(gl.message.sender_address)
        items.append(item)
```

## Example

See [voting.py](../examples/voting.py) for pagination and counter patterns in action.
