"""Binary min-heap written from scratch (priority queue used by both Dijkstra searches)."""
from typing import Any


class MinHeap:
    """Complete binary tree stored in a list: the parent of i is (i - 1) // 2.

    Entries are compared with `<`, so tuples like (cost, vertex_id) work:
    the lowest cost goes first and ties are broken by the id.
    Push and pop are O(log n); peek is O(1).
    """

    def __init__(self) -> None:
        self._items: list[Any] = []

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def peek(self) -> Any:
        """Smallest entry without removing it."""
        if not self._items:
            raise IndexError("peek from an empty heap")
        return self._items[0]

    def push(self, entry: Any) -> None:
        """Add the entry at the end and let it float up to its place."""
        self._items.append(entry)
        self._sift_up(len(self._items) - 1)

    def pop(self) -> Any:
        """Remove and return the smallest entry."""
        if not self._items:
            raise IndexError("pop from an empty heap")
        last = self._items.pop()
        if not self._items:
            return last
        smallest, self._items[0] = self._items[0], last  # the last entry replaces the root
        self._sift_down(0)
        return smallest

    def _sift_up(self, i: int) -> None:
        items = self._items
        while i > 0:
            parent = (i - 1) // 2
            if not items[i] < items[parent]:
                break
            items[i], items[parent] = items[parent], items[i]
            i = parent

    def _sift_down(self, i: int) -> None:
        items, n = self._items, len(self._items)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and items[left] < items[smallest]:
                smallest = left
            if right < n and items[right] < items[smallest]:
                smallest = right
            if smallest == i:
                break
            items[i], items[smallest] = items[smallest], items[i]
            i = smallest
