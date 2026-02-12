# genlayer-utils: storage.py
# TreeMap and DynArray helper functions for GenLayer Intelligent Contracts
#
# Utility functions for common storage operations: pagination, conversion,
# counters. Copy the functions you need into your contract file.
#
# Requires: from genlayer import *

from genlayer import *


def treemap_paginate(
    data: TreeMap,
    offset: int = 0,
    limit: int = 10,
) -> list:
    """
    Paginate a TreeMap. Returns a list of (key, value) tuples.
    Useful for view methods that need to return subsets of large datasets.

    Args:
        data: The TreeMap to paginate
        offset: Number of entries to skip
        limit: Maximum number of entries to return

    Returns:
        List of (key, value) tuples

    Example:
        @gl.public.view
        def get_claims_page(self, page: int) -> list:
            return treemap_paginate(self.claims, offset=page * 10, limit=10)
    """
    items = []
    count = 0
    for k, v in data.items():
        if count < offset:
            count += 1
            continue
        if len(items) >= limit:
            break
        items.append((k, v))
        count += 1
    return items


def treemap_to_list(data: TreeMap) -> list:
    """
    Convert a TreeMap to a list of (key, value) tuples.
    Useful for returning all entries in a view method.

    Args:
        data: The TreeMap to convert

    Returns:
        List of (key, value) tuples

    Example:
        @gl.public.view
        def get_all_entries(self) -> list:
            return treemap_to_list(self.entries)
    """
    return [(k, v) for k, v in data.items()]


def treemap_to_dict(data: TreeMap, *, key_transform=None) -> dict:
    """
    Convert a TreeMap to a plain dict for view method returns.
    Optionally transform keys (e.g., Address -> hex string).

    Args:
        data: The TreeMap to convert
        key_transform: Optional function to transform keys

    Returns:
        A plain Python dict

    Example:
        @gl.public.view
        def get_scores(self) -> dict:
            return treemap_to_dict(self.scores)
    """
    if key_transform:
        return {key_transform(k): v for k, v in data.items()}
    return {k: v for k, v in data.items()}


def address_map_to_dict(data: TreeMap) -> dict:
    """
    Convert a TreeMap[Address, V] to a dict with hex string keys.
    Convenience wrapper for the common pattern of address-keyed maps.

    Args:
        data: TreeMap with Address keys

    Returns:
        Dict with hex string keys

    Example:
        @gl.public.view
        def get_reputation(self) -> dict:
            return address_map_to_dict(self.reputation)
            # Returns: {"0xAbC...": 42, "0xDeF...": 17}
    """
    return {k.as_hex: v for k, v in data.items()}


def increment_or_init(data: TreeMap, key, amount: int = 1) -> None:
    """
    Increment a value in a TreeMap, initializing to 0 if the key is absent.
    Replaces the common 3-line pattern:
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += amount

    Args:
        data: The TreeMap to modify
        key: The key to increment
        amount: How much to add (default: 1)

    Example:
        # Award 10 reputation points
        increment_or_init(self.reputation, sender_address, 10)
    """
    current = data.get(key, 0)
    data[key] = current + amount


def treemap_count(data: TreeMap) -> int:
    """
    Count the number of entries in a TreeMap.
    TreeMap doesn't have a built-in len(), so this iterates.

    Args:
        data: The TreeMap to count

    Returns:
        Number of entries

    Example:
        @gl.public.view
        def total_claims(self) -> int:
            return treemap_count(self.claims)
    """
    count = 0
    for _ in data.items():
        count += 1
    return count
