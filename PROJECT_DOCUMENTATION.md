
# Cafe Management System

## 1. Project Overview

The Cafe Management System is a web-based application designed to help cafe staff manage menu items, create customer orders, calculate bills, and maintain order history.

The project is being developed as a semester PBL project using Python, Flask, SQLite, HTML, CSS, and JavaScript.

## 2. Project Objectives

- Provide a simple interface for managing cafe menu items.
- Validate menu item details before saving them.
- Allow users to create orders from available menu items.
- Calculate order totals accurately.
- Store orders and provide access to order history.
- Apply systematic software testing and defect tracking.

## 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | User interface |
| Backend | Python, Flask | Application routes and business logic |
| Database | SQLite | Persistent application data |
| Testing | pytest | Automated testing |
| Version Control | Git | Source code history and collaboration |
| Project Management | Jira | Task tracking and defect management |

## 4. Functional Requirements

### FR-01: Add Menu Items
The system shall allow a user to add a menu item with a name, category, price, and optional description.

### FR-02: Validate Menu Items
The system shall reject invalid menu data, including missing required fields, invalid prices, and duplicate names.

### FR-03: Edit Menu Items
The system shall allow existing menu item details to be updated.

### FR-04: Delete Menu Items
The system shall allow a menu item to be removed from the active menu.

### FR-05: View and Search Menu Items
The system shall display menu items and allow users to search for relevant items.

### FR-06: Create Orders
The system shall allow users to create an order using available menu items and quantities.

### FR-07: Calculate Bills
The system shall calculate order totals using item prices and selected quantities.

### FR-08: Save Orders
The system shall save completed orders and their associated items.

### FR-09: View Order History
The system shall allow users to view previously saved orders and their totals.

## 5. Non-Functional Requirements

- Usability: The interface should be understandable and easy to navigate.
- Reliability: Invalid input should not corrupt stored data.
- Data integrity: Database constraints should protect required fields and valid values.
- Maintainability: Application code should be separated into logical modules.
- Testability: Core functionality should be verifiable through repeatable test cases.
- Responsiveness: Pages should adapt to desktop and mobile screen sizes.

## 6. System Modules

### Module 1: Menu Management

Responsibilities:
- Add menu items.
- Edit and delete menu items.
- Display and search menu items.
- Validate input and prevent invalid records.

### Module 2: Order and Billing

Responsibilities:
- Create orders from available menu items.
- Select item quantities.
- Calculate totals.
- Save completed orders.

### Module 3: Order History

Responsibilities:
- Store completed order records.
- Retrieve past orders.
- Display order details and totals.

### Module 4: Testing and Delivery

Responsibilities:
- Prepare test cases.
- Execute functional, validation, boundary-value, and integration tests where applicable.
- Record actual results and defects.
- Retest fixes and prepare the final report and demonstration.

## 7. Database Design

### menu_items

| Column | Purpose |
|---|---|
| id | Unique menu item identifier |
| name | Menu item name; unique and required |
| description | Optional item description |
| category | Item category; required |
| price | Item price; must be non-negative |
| available | Availability flag |
| created_at | Record creation timestamp |

The orders and order-items tables will be added when the Order and Billing module is implemented.

## 8. Testing Strategy

Testing will include:
- Functional testing of menu and order workflows.
- Input validation testing.
- Boundary-value analysis for numeric fields such as price and quantity.
- Equivalence partitioning for valid and invalid inputs.
- Integration testing across application and database operations.
- Regression testing after bug fixes.

Test cases will record:
Test Case ID, Module, Scenario, Test Data, Expected Result, Actual Result, and Status.

## 9. Project Deliverables

- Working web application.
- Database schema and application source code.
- Documented requirements and module descriptions.
- Test cases and execution results.
- Defect records and retest evidence where applicable.
- Final project report and demonstration.
