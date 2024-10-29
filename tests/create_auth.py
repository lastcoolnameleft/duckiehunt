import time

from playwright.sync_api import Playwright, sync_playwright, expect
def test_mark_duck(playwright: Playwright) -> None:
    duck_id = '2012'
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    # Go to http://localhost:8001/
    page.goto("http://localhost:8001/")
    input('Hit enter when ready to proceed\n')
    storage = context.storage_state(path="auth.json")

    context.close()
    browser.close()