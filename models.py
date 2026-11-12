
from datetime import date
from uuid import uuid4

class Product:
    def __init__(self, name, category, price, quantity, reorder_level=5,
                 description="", product_id=None):
        self.product_id = product_id or str(uuid4())[:8].upper()
        self.name = str(name).strip()
        self.category = str(category).strip()
        self.price = float(price)
        self.quantity = int(quantity)
        self.reorder_level = int(reorder_level)
        self.description = str(description).strip()

    def total_value(self):
        return round(self.price * self.quantity, 2)

    def stock_status(self):
        if self.quantity <= 0:
            return "Out of stock"
        if self.quantity <= self.reorder_level:
            return "Low stock"
        return "In stock"

    def to_dict(self):
        return {
            "product_id": self.product_id, "name": self.name,
            "category": self.category, "price": self.price,
            "quantity": self.quantity, "reorder_level": self.reorder_level,
            "description": self.description, "total_value": self.total_value(),
            "stock_status": self.stock_status(), "type": "standard"
        }

    @classmethod
    def from_dict(cls, data):
        if data.get("type") == "perishable":
            return PerishableProduct(
                name=data["name"], category=data["category"], price=data["price"],
                quantity=data["quantity"], reorder_level=data.get("reorder_level", 5),
                description=data.get("description", ""),
                expiry_date=data.get("expiry_date", ""), product_id=data["product_id"]
            )
        return cls(
            name=data["name"], category=data["category"], price=data["price"],
            quantity=data["quantity"], reorder_level=data.get("reorder_level", 5),
            description=data.get("description", ""), product_id=data["product_id"]
        )

class PerishableProduct(Product):
    def __init__(self, name, category, price, quantity, reorder_level=5,
                 description="", expiry_date="", product_id=None):
        super().__init__(name, category, price, quantity, reorder_level,
                         description, product_id)
        self.expiry_date = str(expiry_date).strip()

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "perishable"
        data["expiry_date"] = self.expiry_date
        return data
