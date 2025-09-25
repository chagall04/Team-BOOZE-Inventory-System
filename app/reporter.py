from __future__ import annotations

from typing import Dict, Iterable, List

from .models import Inventory, Report, Transaction


class Reporter:
    def __init__(self, inventory: Inventory) -> None:
        raise NotImplementedError

    def generate_low_stock_report(self) -> List[Dict[str, object]]:
        raise NotImplementedError

    def generate_inventory_value_report(self) -> Dict[str, object]:
        raise NotImplementedError


