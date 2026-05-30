import os
import re
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")


def test_homepage_has_Duckiehunt_in_title_and_mark_link(
    page: Page
):
    page.goto(BASE_URL)

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Duckiehunt"))
    
    page.locator("a:has-text(\"Found a Duck?\")").click()
    page.wait_for_url(f"{BASE_URL}/mark/")


def test_mark_new_duck_login(
    page: Page
):
    page.goto(f"{BASE_URL}/mark")

    # Unauthenticated users should see a login link
    login_link = page.locator("a:has-text('Log in')")
    expect(login_link).to_be_visible()

def test_existing_location(
    page: Page
):
    page.goto(f"{BASE_URL}/location/592")

    g_login = page.locator("text=Tommy's Duckie")