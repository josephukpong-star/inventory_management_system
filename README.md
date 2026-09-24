# Inventory Management System

A Python-based inventory management application designed to help businesses manage products, stock levels, categories, inventory value, stock movements, and product lifecycle records.

## Overview

The Inventory Management System provides a structured way to manage inventory through a command-line interface (CLI).

The application uses a layered architecture with separate components for:

* Product models and validation
* Inventory business logic
* Data storage and persistence
* User interface and input handling
* Application control flow
* Automated testing

The project was developed incrementally with a strong focus on validation, error handling, persistence, regression testing, and maintainable Python code.

## Key Capabilities

* Add, view, update, search, and remove products
* Track stock-in and stock-out transactions
* Monitor low-stock and out-of-stock products
* Organize products by category
* Calculate inventory quantities and values
* Generate inventory reports
* View inventory dashboards and alerts
* Track transaction history and transaction values
* Restore removed products
* Permanently delete removed products with an audit record
* Persist inventory state to JSON
* Validate user input and business rules
* Run a comprehensive automated test suite

## Technology Stack

* **Python 3.14**
* **JSON** for inventory data persistence
* **pytest** for automated testing
* **pytest-cov** for test coverage support
* **pytest-mock** for mocking and test isolation
* **Git** for version control
* **GitHub** for source-code hosting

## Project Architecture

The application is organized into separate layers.

### Models

`app/models.py`

Defines the `Product` model and handles product validation, normalization, and serialization.

### Inventory Service

`app/inventory_service.py`

Contains the core inventory business logic, including:

* Product management
* Stock-in and stock-out operations
* Inventory calculations
* Category management
* Inventory alerts
* Dashboard data
* Transaction tracking
* Inventory reports
* Product removal and restoration
* Permanent deletion and audit history

### Storage

`app/storage.py`

Handles JSON-based persistence for:

* Active products
* Transactions
* Removed products
* Deleted-product records
* Deleted-record counters

### User Interface

`app/ui.py`

Provides the command-line interface for:

* Menus
* User input
* Product display
* Inventory summaries
* Dashboard display
* Inventory alerts
* Reports
* Transaction information

### Application

`app/main.py`

Connects the user interface to the inventory service and controls the application workflow.

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/josephukpong-star/inventory_management_system.git
cd inventory_management_system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m app.main
```

The application will start the Inventory Management System command-line interface.

## Usage

After completing the installation steps, start the application with:

```bash
python -m app.main
```

The application displays an interactive command-line menu with the following options:

1. Add Product
2. View Products
3. Search Product
4. Stock In
5. Stock Out
6. Remove Product
7. Inventory Summary
8. Save Inventory
9. Load Inventory
10. Category Summary
11. Inventory Report
12. Transaction History
13. Transaction Summary
14. Transaction Value Summary
15. Exit
16. Dashboard
17. Inventory Alerts
18. Save Inventory Report
19. Update Product
20. View Removed Products
21. Restore Product
22. Permanently Delete Product
23. View Deleted Products History

### Basic Workflow

A typical inventory workflow is:

1. Add products with their ID, name, price, quantity, and category.
2. View or search products when inventory information is needed.
3. Use **Stock In** when additional inventory is received.
4. Use **Stock Out** when products are sold or issued.
5. Monitor **Inventory Summary**, **Dashboard**, and **Inventory Alerts** to track stock health.
6. Use **Transaction History** and transaction summaries to review stock movements.
7. Use **Remove Product** when a product should no longer remain in the active inventory.
8. Use **Restore Product** when a previously removed product needs to be returned to active inventory.
9. Use **Permanently Delete Product** only when a removed product should be permanently deleted.
10. Use **Save Inventory** to persist the current inventory state.
11. Use **Load Inventory** to restore previously saved inventory data.

The application stores inventory data in JSON format and maintains records of inventory transactions and product lifecycle events.

## Testing

The project uses `pytest` for automated testing.

The test suite covers:

* Product validation and serialization
* Inventory management operations
* Stock-in and stock-out transactions
* Inventory calculations
* Category management
* Low-stock and out-of-stock detection
* Inventory reports
* Dashboard and inventory alerts
* Transaction history and summaries
* Product removal and restoration
* Permanent deletion and audit history
* JSON persistence and data recovery
* User interface behavior
* Application control flow
* Error handling and validation rules
* Regression testing for previously identified issues

### Run the full test suite

From the project root:

```bash
pytest -v
```

### Run tests with coverage

```bash
pytest --cov=app --cov-report=term-missing
```

The current project test suite contains **394 automated tests**, all passing at the current development checkpoint.

## Project Structure

```text
inventory_management_system/
│
├── app/
│   ├── __init__.py
│   ├── inventory_service.py
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   └── ui.py
│
├── data/
│   └── inventory.json
│
├── tests/
│   ├── __init__.py
│   ├── test_inventory_service.py
│   ├── test_main.py
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_ui.py
│
├── .gitignore
├── main.py
├── pytest.ini
├── README.md
└── requirements.txt
```

### Directory and File Description

| Path                       | Description                                                |
| -------------------------- | ---------------------------------------------------------- |
| `app/models.py`            | Defines the Product model and validation rules             |
| `app/inventory_service.py` | Contains the core inventory business logic                 |
| `app/storage.py`           | Handles JSON data persistence                              |
| `app/ui.py`                | Handles CLI menus, input, and display                      |
| `app/main.py`              | Controls the application workflow                          |
| `data/inventory.json`      | Stores inventory data                                      |
| `tests/`                   | Contains the automated test suite                          |
| `pytest.ini`               | Configures pytest and the project Python path              |
| `requirements.txt`         | Lists project dependencies                                 |
| `.gitignore`               | Defines files and folders excluded from Git                |
| `main.py`                  | Root application entry point used by the project and tests |
| `README.md`                | Project documentation                                      |