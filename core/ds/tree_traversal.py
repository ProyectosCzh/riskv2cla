class AssetTreeNode:
    def __init__(self, name, children=None, data=None):
        self.name = name
        self.children = children or []
        self.data = data

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def count_descendants(self):
        if self.is_leaf:
            return 1
        return sum(c.count_descendants for c in self.children)


class AssetCategoryTree:
    def __init__(self, assets_data: dict):
        self.root = AssetTreeNode("Todos los Activos")
        self._build(assets_data)

    def _build(self, assets_data: dict):
        for category, items in assets_data.get("categories", {}).items():
            cat_node = AssetTreeNode(category)
            for item in items:
                cat_node.children.append(AssetTreeNode(
                    item["ticker"], data=item
                ))
            self.root.children.append(cat_node)

    def traverse_preorder(self, node=None, depth=0, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        indent = "  " * depth
        if node.is_leaf and node.data:
            icon = {"stock": "📈", "etf": "📦", "bond_etf": "🛡️",
                    "commodity_etf": "🏅", "reit": "🏢"}.get(
                node.data.get("type", ""), "📊")
            result.append({
                "line": f"{indent}{icon} {node.name} — {node.data['name']}",
                "depth": depth,
                "name": node.name,
                "is_leaf": True,
                "data": node.data,
            })
        else:
            icon = "📂" if depth == 0 else "📁"
            result.append({
                "line": f"{indent}{icon} {node.name} ({node.count_descendants} activos)",
                "depth": depth,
                "name": node.name,
                "is_leaf": False,
            })
            for child in node.children:
                self.traverse_preorder(child, depth + 1, result)
        return result

    def traverse_postorder(self, node=None, depth=0, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        if not node.is_leaf:
            for child in node.children:
                self.traverse_postorder(child, depth + 1, result)
        indent = "  " * depth
        if node.is_leaf and node.data:
            result.append(f"{indent}📊 {node.name} — {node.data['name']}")
        else:
            result.append(f"{indent}📁 {node.name} ({node.count_descendants} activos)")
        return result

    def find_by_ticker(self, ticker: str, node=None):
        if node is None:
            node = self.root
        if node.is_leaf and node.data and node.data.get("ticker", "").upper() == ticker.upper():
            return node
        for child in node.children:
            found = self.find_by_ticker(ticker, child)
            if found:
                return found
        return None
