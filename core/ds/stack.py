class _Node:
    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next


class SimulationStack:
    def __init__(self):
        self._top = None
        self._bottom = None
        self._size = 0

    def push(self, item):
        new_node = _Node(item, prev=self._top)
        if self._top:
            self._top.next = new_node
        self._top = new_node
        if self._bottom is None:
            self._bottom = new_node
        self._size += 1

    def pop(self):
        if self._top is None:
            return None
        data = self._top.data
        self._top = self._top.prev
        if self._top:
            self._top.next = None
        else:
            self._bottom = None
        self._size -= 1
        return data

    def peek(self):
        return self._top.data if self._top else None

    def is_empty(self):
        return self._top is None

    def clear(self):
        self._top = None
        self._bottom = None
        self._size = 0

    @property
    def size(self):
        return self._size

    def __len__(self):
        return self._size

    def items(self):
        result = []
        current = self._top
        while current:
            result.append(current.data)
            current = current.prev
        return result

    def __repr__(self):
        items = self.items()
        return f"SimulationStack(top={items[0] if items else None}, size={self._size})"
