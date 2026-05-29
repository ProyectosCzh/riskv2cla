class SimulationSorter:
    ALGORITHM = "MergeSort"

    @staticmethod
    def _get_value(item, key):
        if callable(key):
            return key(item)
        if isinstance(key, str):
            keys = key.split(".")
            val = item
            for k in keys:
                if isinstance(val, dict):
                    val = val.get(k, 0)
                else:
                    return 0
            return val if isinstance(val, (int, float)) else 0
        return getattr(item, key, 0)

    @classmethod
    def merge_sort(cls, items, key="median_capital", reverse=False):
        cls.ALGORITHM = "MergeSort"
        if len(items) <= 1:
            return items[:]

        mid = len(items) // 2
        left = cls.merge_sort(items[:mid], key, reverse)
        right = cls.merge_sort(items[mid:], key, reverse)

        return cls._merge(left, right, key, reverse)

    @staticmethod
    def _merge(left, right, key, reverse):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            a = SimulationSorter._get_value(left[i], key)
            b = SimulationSorter._get_value(right[j], key)
            if (a >= b) if reverse else (a <= b):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    @classmethod
    def quick_sort(cls, items, key="median_capital", reverse=False):
        cls.ALGORITHM = "QuickSort"
        if len(items) <= 1:
            return items[:]

        pivot = cls._get_value(items[-1], key)
        left = []
        right = []
        for item in items[:-1]:
            val = cls._get_value(item, key)
            if (val >= pivot) if reverse else (val <= pivot):
                left.append(item)
            else:
                right.append(item)
        return cls.quick_sort(left, key, reverse) + [items[-1]] + cls.quick_sort(right, key, reverse)

    @classmethod
    def sort(cls, items, key="median_capital", reverse=False):
        if len(items) > 10:
            return cls.quick_sort(items, key, reverse)
        return cls.merge_sort(items, key, reverse)
