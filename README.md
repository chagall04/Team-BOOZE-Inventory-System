# Team-BOOZE Inventory System (MVP)

Simple CLI-driven inventory and sales tracker.

## Structure

```
app/
  __init__.py
  models.py
  inventory_manager.py
  sales_processor.py
  reporter.py
tests/
  test_models.py
  test_inventory.py
main.py
```

## Setup

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
pip install -r requirements.txt
```

## Usage

```bash
python main.py --help
```

Examples:

```bash
python main.py add-product --id 1 --name "Beer" --price 3.5
python main.py stock --id 1 --delta 10
python main.py sell --items 1:2
python main.py report inventory
```

## Testing

```bash
pytest -q
```

