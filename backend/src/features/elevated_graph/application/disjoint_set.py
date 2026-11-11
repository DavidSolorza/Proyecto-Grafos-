"""Disjoint-Set (Union-Find) used by Kruskal to detect cycles."""
from typing import Iterable


class DisjointSet:
    """Groups items in sets. Path compression + union by rank."""

    def __init__(self, items: Iterable[str]) -> None:
        self.parent: dict[str, str] = {x: x for x in items}
        self.rank: dict[str, int] = {x: 0 for x in self.parent}

    def find(self, x: str) -> str:
        """Return the representative (root) of the set containing x."""
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # Path compression: every visited node now points straight to the root
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: str, b: str) -> bool:
        """Merge the sets of a and b. Returns False if they were already joined."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True
