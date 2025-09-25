from __future__ import annotations

from typing import Dict, List

from .models import Inventory, Product


class InventoryManager:
    def __init__(self) -> None:
        raise NotImplementedError

    def add_product(self, product: Product, initial_stock: int = 0) -> None:
        raise NotImplementedError

    def remove_product(self, product: Product) -> None:
        raise NotImplementedError

    def get_product_by_id(self, product_id: int) -> Product:
        raise NotImplementedError

    def update_product(self, product: Product) -> None:
        raise NotImplementedError

    def list_products(self) -> Dict[int, Product]:
        raise NotImplementedError

    def get_stock(self, product_id: int) -> int:
        raise NotImplementedError

    def adjust_stock(self, product_id: int, delta: int) -> int:
        raise NotImplementedError

    def set_stock(self, product_id: int, new_level: int) -> int:
        raise NotImplementedError


