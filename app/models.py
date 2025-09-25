from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class Product:
    product_id: int
    name: str
    price: float
    stock_level: int

    def get_details(self) -> dict:
        """Return product details. Structure TBD."""
        raise NotImplementedError

    def update_stock(self, quantity: int) -> None:
        """Adjust stock level by quantity. Validation TBD."""
        raise NotImplementedError


@dataclass
class TransactionItem:
    item_id: int
    product_id: int
    quantity: int
    price_at_sale: float


@dataclass
class Transaction:
    transaction_id: int
    timestamp: datetime
    total_amount: float
    items: List[TransactionItem]

    def add_item(self, product_id: int, quantity: int) -> None:
        """Append a new TransactionItem to items. Behavior TBD."""
        raise NotImplementedError

    def calculate_total(self) -> float:
        """Compute total amount from items. Behavior TBD."""
        raise NotImplementedError


@dataclass
class Inventory:
    products: List[Product]

    def add_product(self, product: Product) -> None:
        """Add a Product to the inventory. Behavior TBD."""
        raise NotImplementedError

    def remove_product(self, product: Product) -> None:
        """Remove a Product from the inventory. Behavior TBD."""
        raise NotImplementedError

    def get_product_by_id(self, product_id: int) -> Product:
        """Retrieve a product by its integer ID. Behavior TBD."""
        raise NotImplementedError


@dataclass
class Report:
    inventory_data: Dict[str, object]
    transaction_data: Dict[str, object]

    def generate_low_stock_report(self) -> List[Dict[str, object]]:
        """Return rows describing low-stock items. Criteria TBD."""
        raise NotImplementedError

    def generate_inventory_value_report(self) -> Dict[str, object]:
        """Aggregate inventory value metrics. Calculation TBD."""
        raise NotImplementedError


