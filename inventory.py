
import json
import os
from models import Product, PerishableProduct

class InventoryManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.products = []
        self.load_inventory()

    @staticmethod
    def _validated(data, existing=None):
        name = str(data.get("name", existing.name if existing else "")).strip()
        category = str(data.get("category", existing.category if existing else "")).strip()
        if not name or not category:
            raise ValueError("Product name and category are required.")
        try:
            price = float(data.get("price", existing.price if existing else 0))
            quantity = int(data.get("quantity", existing.quantity if existing else 0))
            reorder = int(data.get("reorder_level", existing.reorder_level if existing else 5))
        except (TypeError, ValueError):
            raise ValueError("Price, quantity and reorder level must be valid numbers.")
        if price < 0 or quantity < 0 or reorder < 0:
            raise ValueError("Price, quantity and reorder level cannot be negative.")
        if price > 100000000 or quantity > 100000000:
            raise ValueError("Please enter a smaller value.")
        return name, category, price, quantity, reorder

    def load_inventory(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            self.products = []
            self.save_inventory()
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                records = json.load(file)
            self.products = [Product.from_dict(item) for item in records]
        except (json.JSONDecodeError, KeyError, TypeError):
            self.products = []

    def save_inventory(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        temp = self.data_file + ".tmp"
        with open(temp, "w", encoding="utf-8") as file:
            json.dump([p.to_dict() for p in self.products], file, indent=2)
        os.replace(temp, self.data_file)

    def add_product(self, data):
        name, category, price, quantity, reorder = self._validated(data)
        common = dict(name=name, category=category, price=price, quantity=quantity,
                      reorder_level=reorder, description=data.get("description", ""))
        if data.get("type") == "perishable":
            product = PerishableProduct(**common, expiry_date=data.get("expiry_date", ""))
        else:
            product = Product(**common)
        self.products.append(product)
        self.save_inventory()
        return product.to_dict()

    def get_all_products(self):
        return [p.to_dict() for p in self.products]

    def find_product(self, product_id):
        return next((p for p in self.products if p.product_id == product_id), None)

    def update_product(self, product_id, data):
        old = self.find_product(product_id)
        if not old:
            return None
        merged = old.to_dict()
        merged.update(data)
        name, category, price, quantity, reorder = self._validated(merged, old)
        common = dict(name=name, category=category, price=price, quantity=quantity,
                      reorder_level=reorder, description=merged.get("description", ""),
                      product_id=product_id)
        if merged.get("type") == "perishable":
            updated = PerishableProduct(**common, expiry_date=merged.get("expiry_date", ""))
        else:
            updated = Product(**common)
        self.products[self.products.index(old)] = updated
        self.save_inventory()
        return updated.to_dict()

    def delete_product(self, product_id):
        product = self.find_product(product_id)
        if not product:
            return False
        self.products.remove(product)
        self.save_inventory()
        return True

    def search_products(self, query):
        q = query.lower()
        return [p.to_dict() for p in self.products if
                q in p.name.lower() or q in p.category.lower() or q in p.product_id.lower()]

    def low_stock_products(self):
        return [p.to_dict() for p in self.products if 0 < p.quantity <= p.reorder_level]

    def out_of_stock_products(self):
        return [p.to_dict() for p in self.products if p.quantity == 0]

    def get_statistics(self):
        return {
            "total_products": len(self.products),
            "total_units": sum(p.quantity for p in self.products),
            "inventory_value": round(sum(p.total_value() for p in self.products), 2),
            "low_stock": len(self.low_stock_products()),
            "out_of_stock": len(self.out_of_stock_products())
        }
