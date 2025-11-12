import pytest
import time
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"
USER1 = {"username": "user1", "password": "letstest1"}
USER2 = {"username": "user2", "password": "letstest2"}

@pytest.fixture(scope="function")
def browser_context(page: Page):
    """Setup: Navigate to login page before each test"""
    page.goto(f"{BASE_URL}/login/")
    yield page

def login(page: Page, username: str, password: str):
    """Helper function to perform login"""
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    expect(page).to_have_url(f"{BASE_URL}/dashboard/")

def logout(page: Page):
    """Helper function to logout"""
    page.get_by_role("link", name="Logout").click()
    expect(page).to_have_url(f"{BASE_URL}/login/")

def add_task(page: Page, task_name: str):
    """Helper function to add a new task"""
    page.fill('input[name="title"]', task_name)
    page.click('button[type="submit"]') 
    expect(page.locator(f'.list-group-item:has-text("{task_name}")')).to_be_visible()
 
def clear_all_tasks(page: Page):
    """Delete all visible tasks"""
    while page.locator('button[title="Delete task"]').count() > 0:
        page.locator('button[title="Delete task"]').first.click()
        page.wait_for_load_state('networkidle')

def test_login_success(browser_context: Page):
    """Test successful login redirects to dashboard"""
    page = browser_context
    login(page, USER1["username"], USER1["password"])

def test_add_task(browser_context: Page):
    """Test adding a new task"""
    page = browser_context
    login(page, USER1["username"], USER1["password"])
    task_name = f"Test Task {int(time.time())}"
    add_task(page, task_name)
    clear_all_tasks(page)

def test_complete_task(browser_context: Page):
    """Test marking a task as completed"""
    page = browser_context
    login(page, USER1["username"], USER1["password"])
    task_name = f"Complete Test {int(time.time())}"
    add_task(page, task_name)
    task_item = page.locator(f'.list-group-item:has-text("{task_name}")').first
    task_item.locator('button[title="Mark as completed"]').click()
    task_span = task_item.locator(f'span:has-text("{task_name}")')
    expect(task_span).to_have_class("text-decoration-line-through text-muted")
    clear_all_tasks(page)

def test_delete_task(browser_context: Page):
    """Test deleting a task"""
    page = browser_context
    login(page, USER1["username"], USER1["password"])
    task_name = f"Delete Test {int(time.time())}"
    add_task(page, task_name)
    
    # Verify task exists
    expect(page.locator(f'.list-group-item:has-text("{task_name}")')).to_be_visible()
    
    # Delete the task
    task_item = page.locator(f'.list-group-item:has-text("{task_name}")').first
    delete_btn = task_item.locator('button[title="Delete task"]')
    delete_btn.click()
    
    # Wait for page reload
    page.wait_for_load_state('networkidle')
    
    # Verify task is gone
    expect(page.locator(f'.list-group-item:has-text("{task_name}")')).not_to_be_visible()

def test_data_isolation(browser_context: Page):
    """
    Verify users can only see their own tasks
    BUG: User 2 can see User 1's tasks
    """
   
    page = browser_context

    # Login as USER1
    login(page, USER1["username"], USER1["password"])

    # Add tasks for USER1
    user1_tasks = [
        f"User1 Task 1 {int(time.time())}",
        f"User1 Task 2 {int(time.time())}"
    ]
    for task in user1_tasks:
        add_task(page, task)

    # Verify USER1's tasks are visible
    for task in user1_tasks:
        expect(page.locator(f'.list-group-item:has-text("{task}")')).to_be_visible()

    # Logout
    logout(page)

    # Step 5: Login as USER2
    login(page, USER2["username"], USER2["password"])

    for task in user1_tasks:
        task_locator = page.locator(f'.list-group-item:has-text("{task}")')
        
        # This assertion SHOULD pass but FAILS due to the bug
        try:
            expect(task_locator).not_to_be_visible()
            print(f"PASS: '{task}' correctly NOT visible to USER2")
        except AssertionError:
            print(f"FAIL: '{task}' is visible to USER2 (BUG CONFIRMED)")
            raise AssertionError(f"Data Isolation Bug: USER2 can see USER1's task '{task}'")

    # Add tasks for USER2
    user2_tasks = [
        f"User2 Task Gamma {int(time.time())}",
        f"User2 Task Delta {int(time.time())}"
    ]
    for task in user2_tasks:
        add_task(page, task)

    # Verify only USER2's tasks are visible
    for task in user2_tasks:
        expect(page.locator(f'.list-group-item:has-text("{task}")')).to_be_visible()
    
    # USER1's tasks should still not be visible
    for task in user1_tasks:
        try:
            expect(page.locator(f'.list-group-item:has-text("{task}")')).not_to_be_visible()
        except AssertionError:
            print(f" FAIL: USER1's task '{task}' still visible after USER2 added tasks")
            raise

def test_pagination(browser_context: Page):
    """Test tasks shouldn't disappear when paginating"""
    page = browser_context
    login(page, USER1["username"], USER1["password"])
    
    for i in range(6):
        add_task(page, f"Task{i}:{int(time.time())}")
    
    # Go to page 2 if it exists
    page.reload()
    if page.locator('a:has-text("Next")').count() > 0:
        page.locator('a:has-text("Next")').click()
        page.wait_for_load_state('networkidle')
        
        # Should have at least 1 task on page 2
        task_count = page.locator('.list-group-item').count()
        assert task_count >= 1, "BUG: No tasks on page 2 - task disappeared!"
    clear_all_tasks(page)