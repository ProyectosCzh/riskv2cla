class _Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class DownloadQueue:
    def __init__(self):
        self._front = None
        self._rear = None
        self._size = 0

    def enqueue(self, item):
        new_node = _Node(item)
        if self._rear:
            self._rear.next = new_node
        self._rear = new_node
        if self._front is None:
            self._front = new_node
        self._size += 1

    def dequeue(self):
        if self._front is None:
            return None
        data = self._front.data
        self._front = self._front.next
        if self._front is None:
            self._rear = None
        self._size -= 1
        return data

    def peek(self):
        return self._front.data if self._front else None

    def is_empty(self):
        return self._front is None

    def clear(self):
        self._front = None
        self._rear = None
        self._size = 0

    @property
    def size(self):
        return self._size

    def __len__(self):
        return self._size

    def __iter__(self):
        current = self._front
        while current:
            yield current.data
            current = current.next

    def __repr__(self):
        items = list(self)
        return f"DownloadQueue({' -> '.join(str(i) for i in items)})"
