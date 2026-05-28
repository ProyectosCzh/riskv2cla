import json
import pytest
import os
from pathlib import Path

from core.ds.queue import DownloadQueue
from core.ds.stack import SimulationStack
from core.ds.sorting import SimulationSorter
from core.ds.tree_traversal import AssetCategoryTree, AssetTreeNode


# ── DownloadQueue Tests ────────────────────────────────────────────────────────

class TestDownloadQueue:
    def test_enqueue_dequeue(self):
        q = DownloadQueue()
        q.enqueue("AAPL")
        q.enqueue("MSFT")
        q.enqueue("GOOGL")
        assert q.size == 3
        assert q.dequeue() == "AAPL"
        assert q.dequeue() == "MSFT"
        assert q.dequeue() == "GOOGL"
        assert q.is_empty()

    def test_peek(self):
        q = DownloadQueue()
        q.enqueue("SPY")
        assert q.peek() == "SPY"
        assert q.size == 1
        q.dequeue()
        assert q.peek() is None

    def test_empty_queue(self):
        q = DownloadQueue()
        assert q.is_empty()
        assert q.size == 0
        assert q.dequeue() is None
        assert q.peek() is None

    def test_clear(self):
        q = DownloadQueue()
        q.enqueue("A")
        q.enqueue("B")
        q.clear()
        assert q.is_empty()
        assert q.size == 0

    def test_iteration(self):
        q = DownloadQueue()
        q.enqueue("X")
        q.enqueue("Y")
        q.enqueue("Z")
        items = list(q)
        assert items == ["X", "Y", "Z"]
        assert q.size == 3

    def test_fifo_order(self):
        q = DownloadQueue()
        for i in range(5):
            q.enqueue(i)
        results = []
        while not q.is_empty():
            results.append(q.dequeue())
        assert results == [0, 1, 2, 3, 4]

    def test_repr(self):
        q = DownloadQueue()
        q.enqueue("A")
        q.enqueue("B")
        r = repr(q)
        assert "A" in r
        assert "B" in r


# ── SimulationStack Tests ──────────────────────────────────────────────────────

class TestSimulationStack:
    def test_push_pop(self):
        s = SimulationStack()
        s.push({"id": 1, "median": 100})
        s.push({"id": 2, "median": 200})
        assert s.size == 2
        assert s.pop()["id"] == 2
        assert s.pop()["id"] == 1
        assert s.is_empty()

    def test_peek(self):
        s = SimulationStack()
        s.push("first")
        s.push("second")
        assert s.peek() == "second"
        assert s.size == 2

    def test_empty_stack(self):
        s = SimulationStack()
        assert s.is_empty()
        assert s.size == 0
        assert s.pop() is None
        assert s.peek() is None

    def test_clear(self):
        s = SimulationStack()
        s.push(1)
        s.push(2)
        s.push(3)
        s.clear()
        assert s.is_empty()

    def test_lifo_order(self):
        s = SimulationStack()
        for i in range(5):
            s.push(i)
        results = []
        while not s.is_empty():
            results.append(s.pop())
        assert results == [4, 3, 2, 1, 0]

    def test_items_returns_top_first(self):
        s = SimulationStack()
        s.push("first")
        s.push("second")
        s.push("third")
        items = s.items()
        assert items == ["third", "second", "first"]


# ── SimulationSorter Tests ─────────────────────────────────────────────────────

class TestSimulationSorter:
    @pytest.fixture
    def sample_sims(self):
        return [
            {"id": "a", "summary": {"median_capital": 50000, "cagr_median": 0.05}},
            {"id": "b", "summary": {"median_capital": 80000, "cagr_median": 0.08}},
            {"id": "c", "summary": {"median_capital": 30000, "cagr_median": 0.03}},
            {"id": "d", "summary": {"median_capital": 100000, "cagr_median": 0.10}},
        ]

    def test_merge_sort_ascending(self, sample_sims):
        def key_fn(s):
            return s["summary"]["median_capital"]
        result = SimulationSorter.merge_sort(sample_sims, key=key_fn, reverse=False)
        values = [s["summary"]["median_capital"] for s in result]
        assert values == [30000, 50000, 80000, 100000]

    def test_merge_sort_descending(self, sample_sims):
        def key_fn(s):
            return s["summary"]["median_capital"]
        result = SimulationSorter.merge_sort(sample_sims, key=key_fn, reverse=True)
        values = [s["summary"]["median_capital"] for s in result]
        assert values == [100000, 80000, 50000, 30000]

    def test_quick_sort_ascending(self, sample_sims):
        def key_fn(s):
            return s["summary"]["cagr_median"]
        result = SimulationSorter.quick_sort(sample_sims, key=key_fn, reverse=False)
        values = [s["summary"]["cagr_median"] for s in result]
        assert values == [0.03, 0.05, 0.08, 0.10]

    def test_quick_sort_descending(self, sample_sims):
        def key_fn(s):
            return s["summary"]["cagr_median"]
        result = SimulationSorter.quick_sort(sample_sims, key=key_fn, reverse=True)
        values = [s["summary"]["cagr_median"] for s in result]
        assert values == [0.10, 0.08, 0.05, 0.03]

    def test_sort_uses_quicksort_for_large(self, sample_sims):
        large_list = sample_sims * 5
        def key_fn(s):
            return s["summary"]["median_capital"]
        result = SimulationSorter.sort(large_list, key=key_fn, reverse=True)
        assert len(result) == 20
        assert SimulationSorter.ALGORITHM == "QuickSort"

    def test_sort_uses_mergesort_for_small(self, sample_sims):
        def key_fn(s):
            return s["summary"]["median_capital"]
        result = SimulationSorter.sort(sample_sims, key=key_fn, reverse=False)
        assert len(result) == 4
        assert SimulationSorter.ALGORITHM == "MergeSort"

    def test_single_element(self):
        def key_fn(s):
            return s["x"]
        result = SimulationSorter.merge_sort([{"x": 42}], key=key_fn)
        assert result[0]["x"] == 42

    def test_empty_list(self):
        result = SimulationSorter.quick_sort([], key=lambda x: x)
        assert result == []


# ── AssetCategoryTree Tests ────────────────────────────────────────────────────

class TestAssetCategoryTree:
    @pytest.fixture
    def sample_data(self):
        return {
            "categories": {
                "Acciones": [
                    {"ticker": "AAPL", "name": "Apple Inc.", "type": "stock"},
                    {"ticker": "MSFT", "name": "Microsoft", "type": "stock"},
                ],
                "ETFs": [
                    {"ticker": "SPY", "name": "SPDR S&P 500", "type": "etf"},
                    {"ticker": "QQQ", "name": "Invesco QQQ", "type": "etf"},
                    {"ticker": "BND", "name": "Vanguard Bond", "type": "bond_etf"},
                ],
            }
        }

    def test_build_tree(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        assert tree.root.name == "Todos los Activos"
        assert len(tree.root.children) == 2

    def test_count_descendants(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        assert tree.root.count_descendants == 5

    def test_preorder_traversal(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        result = tree.traverse_preorder()
        assert len(result) == 1 + 2 + 5
        assert result[0]["name"] == "Todos los Activos"
        leaf_names = [e["name"] for e in result if e["is_leaf"]]
        assert "AAPL" in leaf_names
        assert "BND" in leaf_names

    def test_postorder_traversal(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        result = tree.traverse_postorder()
        assert len(result) == 1 + 2 + 5
        assert "Todos los Activos" in result[-1]

    def test_find_by_ticker(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        node = tree.find_by_ticker("AAPL")
        assert node is not None
        assert node.data["name"] == "Apple Inc."

    def test_find_by_ticker_case_insensitive(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        node = tree.find_by_ticker("aapl")
        assert node is not None

    def test_find_nonexistent_ticker(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        assert tree.find_by_ticker("ZZZZ") is None

    def test_is_leaf_property(self, sample_data):
        tree = AssetCategoryTree(sample_data)
        assert tree.root.is_leaf is False
        leaf_node = tree.root.children[0].children[0]
        assert leaf_node.is_leaf is True

    def test_asset_tree_node_init(self):
        node = AssetTreeNode("Test", data={"ticker": "TST"})
        assert node.name == "Test"
        assert node.data["ticker"] == "TST"
        assert node.is_leaf
