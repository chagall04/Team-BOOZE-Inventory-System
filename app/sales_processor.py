from __future__ import annotations

from typing import List

from .models import Inventory, Transaction, TransactionItem


class SalesProcessor:
    def __init__(self, inventory: Inventory) -> None:
        raise NotImplementedError

    def process_sale(self, transaction_id: int, items: List[TransactionItem]) -> Transaction:
        raise NotImplementedError


