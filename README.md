# QA Automation Test Submission

## Overview

This repository contains automated end-to-end tests for the Django Todo App challenge. The test suite validates core functionality including authentication, task management, data isolation, and pagination using Playwright with Pytest.

## Setup & Running Tests
### 1. Clone or Download the Project

```bash
cd todo_app
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

### 6. Run tests using pytest

```bash
pytest --headed
```

## Test Coverage
- ✅ Login functionality
- ✅ Task creation, completion and deletion operations
- ✅ Data isolation between users
- ✅ Pagination

## Bugs Found

### BUG1: Data Isolation Failure
**Description:** Users could view ALL tasks in the system regardless of who created them. User 2 could see User 1's private tasks on their dashboard.

**Root Cause:**  The dashboard view in views.py fetches ALL tasks instead of filtering by user: tasks = Task.objects.all()

**Fix Applied:** Filter tasks by logged-in user: tasks = Task.objects.filter(user=request.user)

**Verified By:**  test_data_isolation()

### BUG2: Pagination Issue

**Description:** Tasks on page 2 were not visible

**Root Cause:**  Off-by-one error in pagination offset calculation: start = (page + 1) * ITEMS_PER_PAGE

**Fix Applied:** Corrected pagination offset calculation: start = page * ITEMS_PER_PAGE

**Verified By:** test_pagination()

### Application Code Fixed:

- views.py - Fixed data isolation and pagination bugs

### Test Files Created:

- tests_e2e.py - Complete end-to-end test suite

## Future scope

### Due to limited time, the following improvements are recommended for a production-ready suite:
- Add more test cases for edge and negative scenarios (e.g., empty task list, invalid inputs).
- Separate test files for modularity and easier maintenance (login, CRUD, data isolation, pagination).
- Detailed pagination tests covering multiple pages and boundary conditions.
- Continuous Integration setup to automatically run tests and generate coverage reports.
