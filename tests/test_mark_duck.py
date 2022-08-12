from playwright.sync_api import Playwright, sync_playwright, expect
def test_mark_duck(playwright: Playwright) -> None:
    duck_id = '2012'
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    # Open new page
    page = context.new_page()
    # Go to http://localhost:81/
    page.goto("http://localhost:81/")
    # Click a:has-text("Update a duck")
    page.locator("a:has-text(\"Update a duck\")").click()
    page.wait_for_url("http://localhost:81/mark/")
    # Click input[name="duck_id"]
    page.locator("input[name=\"duck_id\"]").click()
    # Fill input[name="duck_id"]
    page.locator("input[name=\"duck_id\"]").fill(duck_id)
    # Click .col-sm-10 >> nth=0
    page.locator(".col-sm-10").first.click()
    # Click input[name="name"]
    page.locator("input[name=\"name\"]").click()
    # Fill input[name="name"]
    page.locator("input[name=\"name\"]").fill("Duck " + duck_id)
    # Click [placeholder="Enter a location"]
    page.locator("[placeholder=\"Enter a location\"]").click()
    # Fill [placeholder="Enter a location"]
    page.locator("[placeholder=\"Enter a location\"]").fill("cut off")
    # Click text=Cut OffLA, USA
    page.locator("text=Cut OffLA, USA").click()
    # Click textarea[name="comments"]
    page.locator("textarea[name=\"comments\"]").click()
    # Fill textarea[name="comments"]
    page.locator("textarea[name=\"comments\"]").fill("test")
    # Click dt:has-text("Comments/Story:")
    page.locator("dt:has-text(\"Comments/Story:\")").click()
    # Click text=Submit new location
    page.locator("text=Submit new location").click()
    page.wait_for_url("http://localhost:81/location/**")

    # test stuff
    duck_name = page.locator("#duck_name")
    expect(duck_name).to_contain_text("Duck " + duck_id)
    # ---------------------
    context.close()
    browser.close()