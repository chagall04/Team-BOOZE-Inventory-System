# Team BOOZE Inventory System

> | A Liquor Store Inventory Management System

## Project Overview

This repository contains the source code for the Liquor Store Inventory Management System, a project for the Software Engineering 3 module.

The system provides core inventory tracking, product management, sales processing, and reporting for a small-to-medium-sized liquor store. Development follows an agile process with emphasis on code quality, thorough testing, and continuous integration/continuous delivery (CI/CD).

---

## Features

### Core Modules

| Module | Description |
|--------|-------------|
| **Product Management** | Add, view, update, and search products in the catalog |
| **Inventory Tracking** | Manage stock levels, receive shipments, log product losses |
| **Sales Management** | Process sales, view transaction history, print receipts |
| **Reporting & Analytics** | Generate low-stock reports, inventory value, export to CSV/JSON |
| **User Authentication** | Role-based access control (Manager/Clerk) with secure login |

### Manager Features
- Add/Update Products
- View Low Stock Report (with customizable threshold)
- View Sales History
- View Transaction Details
- View Total Inventory Value
- Export Reports (CSV/JSON)

### Clerk Features
- Record Sales (with receipt printing)
- Receive New Stock
- View Product Stock
- Log Product Loss
- View Transaction Details
- View Last Sale

### User Experience
- 🎨 **Colour-coded CLI** - Intuitive colored menus and messages
- 📊 **Dashboard** - Quick stats displayed on login (total products, inventory value, today's sales, low stock items)
- 🔐 **Secure Password Input** - Hidden password entry using `getpass`
- 👤 **Session Display** - Shows logged-in user and role in menu headers
- ⌨️ **Quick Cancel** - Enter `[Q]` to quit/cancel any operation
- ✅ **Confirmation Prompts** - Before destructive actions (delete account, exit)
- 🔠 **Flexible Input** - Case-insensitive menu choices, `Y/N` or `yes/no` for confirmations
- 💬 **Helpful Error Messages** - Specific errors with actionable hints

---

## Getting Started

### Prerequisites

- Python 3.x
- `pip` for package management
- SQLite (included with Python)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/chagall04/Team-BOOZE-Inventory-System.git
   cd Team-BOOZE-Inventory-System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the application:
```bash
python -m src.app
```

#### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Manager | `manager` | `manager123` |
| Clerk | `clerk` | `clerk123` |

---

## Development

### Running Tests
```bash
python -m pytest --cov=src --cov-report=term-missing
```

### Linting
```bash
python -m pylint src --max-line-length=120
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `bcrypt` | Secure password hashing |
| `colorama` | Cross-platform colored terminal output |
| `pytest` | Testing framework |
| `pytest-cov` | Code coverage reporting |
| `pylint` | Static code analysis |

---

## Project Structure

```
Team-BOOZE-Inventory-System/
├── src/
│   ├── app.py                 # Main CLI application & menus
│   ├── auth.py                # User authentication & account management
│   ├── database_manager.py    # Database operations (SQLite)
│   ├── inventory_tracking.py  # Stock management functions
│   ├── product_management.py  # Product CRUD operations
│   ├── reporting.py           # Reports & export functionality
│   └── sales.py               # Sales processing & transaction history
├── tests/
│   ├── test_app.py
│   ├── test_auth.py
│   ├── test_database_manager.py
│   ├── test_inventory_tracking.py
│   ├── test_product_management.py
│   ├── test_reporting.py
│   └── test_sales.py
├── requirements.txt
├── Jenkinsfile
└── README.md
```

---

## Documentation & Project Management

- **Jira Board**: [Backlog & Sprints](https://software-engineering-project-2025-sem1.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)
- **Confluence Wiki**: [Design & Reports](https://software-engineering-project-2025-sem1.atlassian.net/wiki/spaces/TITS/overview?homepageId=66124)
  - Project Overview
  - Architecture & Design Document
  - Requirements Package

---

## Quality Metrics

- ✅ **317+ tests** passing
- ✅ **98% code coverage**
- ✅ **Pylint 10/10** rating
- ✅ **SonarCloud** quality gate passed

---

## Contributors

- Charlie Gallagher
- Lucy O'Connor
- Séan Bardon
- Sara Larkem

---

## License

This project is developed for educational purposes as part of the Software Engineering 3 module.
