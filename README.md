# Team BOOZE Inventory System

## Project Overview

This repository contains the source code for the Liquor Store Inventory Management System, a project for the Software Engineering 3 module.

The system is designed to provide core inventory tracking, product management, and sales processing for a small-to-medium-sized liquor store. Development follows an agile process, emphasizing code quality, thorough testing, and continuous integration/continuous delivery (CI/CD).

---

## Features

The **Minimum Viable Product (MVP)** is structured around four core functionalities:

-   **Product Management**: Functions to add, view, and update products in the catalog.
-   **Inventory Tracking**: Logic to manage stock levels (receiving new shipments, logging losses).
-   **Sales Transaction Management**: Processing sales and recording transaction history.
-   **Reporting & Analytics**: Generating basic reports, such as low-stock and total inventory value.

---

## Getting Started

### Prerequisites

-   Python 3.x
-   `pip` for package management
-   A local environment for database (SQLite for MVP).

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/chagall04/Team-BOOZE-Inventory-System.git](https://github.com/chagall04/Team-BOOZE-Inventory-System.git)
    cd Team-BOOZE-Inventory-System
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

The application uses a Command Line Interface (CLI) with colored output.

Run the application:
```bash
python -m src.app
```

#### Default Login Credentials
- **Manager**: username `manager`, password `manager123`
- **Clerk**: username `clerk`, password `clerk123`

#### Features
- 📊 Dashboard with quick stats on login
- 🔐 Secure password input (hidden when typing)
- 🎨 Color-coded menus and messages
- ⌨️ `[Q]` to quit/cancel any operation
- ✓ Confirmation prompts for destructive actions

-----

## Documentation and Project Management

  - **Jira Board (Backlog & Sprints)**: https://software-engineering-project-2025-sem1.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog
  - **Confluence Wiki (Design & Reports)**: https://software-engineering-project-2025-sem1.atlassian.net/wiki/spaces/TITS/overview?homepageId=66124
      * This includes the Project Overview, Architecture & Design Document & Requirements Package.

-----

## Contributors

  - Charlie Gallagher
  - Lucy O'Connor
  - Séan Bardon
  - Sara Larkem
