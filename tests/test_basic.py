import re
from playwright.sync_api import Page, expect


def test_homepage_has_Duckiehunt_in_title_and_mark_link(
    page: Page
):
    page.goto("http://localhost:8001")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Duckiehunt"))
    
    page.locator("a:has-text(\"Mark a duck\")").click()
    page.wait_for_url("http://localhost:8001/login?next=/mark/")


def test_mark_new_duck_login(
    page: Page
):
    page.goto("http://localhost:8001/mark")

    g_login = page.locator("text=Google")
    expect(g_login).to_have_attribute("href", "/oauth/login/google-oauth2/")
    fb_login = page.locator("text=Facebook")
    expect(fb_login).to_have_attribute("href", "/oauth/login/facebook/")

def test_existing_location(
    page: Page
):
    page.goto("http://localhost:8001/location/592")

    g_login = page.locator("text=Tommy's Duckie")