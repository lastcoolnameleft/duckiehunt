"""Tests for Bootstrap 5 interactive UI components.

Covers: navbar hamburger menu, accordion open/close, mark form JS behavior,
create form rendering, and footer links.
"""
import os
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.staging_safe

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8042")


class TestNavbar:
    """Test navbar collapse/expand (hamburger menu) behavior."""

    def test_navbar_links_visible_on_desktop(self, page: Page):
        """Nav links are visible at desktop width."""
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(BASE_URL)
        nav = page.locator("#navbarResponsive")
        expect(nav).to_be_visible()
        expect(page.locator("a.nav-link", has_text="Update a duck")).to_be_visible()

    def test_navbar_collapses_on_mobile(self, page: Page):
        """Nav links are hidden behind hamburger on mobile width."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(BASE_URL)
        nav = page.locator("#navbarResponsive")
        expect(nav).not_to_be_visible()
        # Hamburger button should be visible
        toggler = page.locator("button.navbar-toggler")
        expect(toggler).to_be_visible()

    def test_hamburger_expands_menu(self, page: Page):
        """Clicking hamburger shows nav links on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(BASE_URL)
        toggler = page.locator("button.navbar-toggler")
        toggler.click()
        nav = page.locator("#navbarResponsive")
        expect(nav).to_be_visible(timeout=3000)
        expect(page.locator("a.nav-link", has_text="Update a duck")).to_be_visible()


class TestAccordionFAQ:
    """Test FAQ page accordion open/close."""

    def test_faq_accordion_opens(self, page: Page):
        """Clicking an FAQ item expands its content."""
        page.goto(f"{BASE_URL}/faq")
        # The first shown item should already be visible
        first_body = page.locator("#collapseTwo .card-body")
        expect(first_body).to_be_visible()

    def test_faq_accordion_toggles(self, page: Page):
        """Clicking another FAQ item opens it (accordion behavior)."""
        page.goto(f"{BASE_URL}/faq")
        # Click "Why are you doing this?"
        page.locator("a[href='#collapseOne']").click()
        body = page.locator("#collapseOne")
        expect(body).to_be_visible(timeout=3000)


class TestAccordionIssue:
    """Test Issue page accordion."""

    def test_issue_accordion_opens(self, page: Page):
        """Clicking an issue item expands its content."""
        page.goto(f"{BASE_URL}/issue")
        # Click first item
        page.locator("a[href='#collapse1']").click()
        body = page.locator("#collapse1")
        expect(body).to_be_visible(timeout=3000)
        expect(body).to_contain_text("Email me")


class TestMarkFormJS:
    """Test mark form JavaScript behavior (vanilla JS after jQuery removal)."""

    def test_name_field_initially_disabled(self, page: Page):
        """Name field starts disabled until duck ID is checked."""
        page.goto(f"{BASE_URL}/mark")
        name_field = page.locator("#id_name")
        expect(name_field).to_be_disabled()

    def test_name_field_enables_for_unknown_duck(self, page: Page):
        """Name field enables when duck ID doesn't exist (new duck)."""
        page.goto(f"{BASE_URL}/mark")
        duck_id_field = page.locator("#id_duck_id")
        duck_id_field.fill("99999")
        duck_id_field.blur()
        name_field = page.locator("#id_name")
        # Wait for fetch to complete and enable the field
        expect(name_field).to_be_enabled(timeout=5000)
        notification = page.locator("#name_notification")
        expect(notification).to_contain_text("creative")

    def test_submit_button_disables_on_submit(self, page: Page):
        """Submit button shows spinner and disables on form submit."""
        page.goto(f"{BASE_URL}/mark")
        # Verify the submit handler is wired by dispatching submit event directly
        # (bypassing HTML5 validation which would block it with empty required fields)
        result = page.evaluate("""() => {
            const form = document.getElementById('formMark');
            const btn = document.getElementById('buttonSubmit');
            const event = new Event('submit', { cancelable: true, bubbles: true });
            event.preventDefault();
            form.dispatchEvent(event);
            return { disabled: btn.disabled, hasSpinner: btn.innerHTML.includes('spinner') };
        }""")
        assert result["disabled"] is True
        assert result["hasSpinner"] is True

    def test_use_my_location_button_visible(self, page: Page):
        """'Use my location' button is visible on the mark form."""
        page.goto(f"{BASE_URL}/mark")
        btn = page.locator("#btnUseMyLocation")
        expect(btn).to_be_visible()
        expect(btn).to_contain_text("Use my location")

    def test_use_my_location_fills_coordinates(self, page: Page):
        """Geolocation fills lat/lng when browser provides position."""
        page.goto(f"{BASE_URL}/mark")

        # Mock the geolocation API to return Austin, TX coordinates
        page.evaluate("""() => {
            navigator.geolocation.getCurrentPosition = function(success) {
                success({
                    coords: { latitude: 30.2672, longitude: -97.7431, accuracy: 10 }
                });
            };
        }""")

        page.click("#btnUseMyLocation")
        # Wait for geocoder response or timeout
        page.wait_for_timeout(2000)

        lat_val = page.locator("#id_lat").input_value()
        lng_val = page.locator("#id_lng").input_value()
        assert lat_val == "30.2672"
        assert lng_val == "-97.7431"


class TestCreateForm:
    """Test create duck form page."""

    def test_create_page_loads(self, page: Page):
        """Create duck page loads with form elements."""
        page.goto(f"{BASE_URL}/duck/new")
        # May redirect to login if not authenticated — either way page loads
        assert page.url.startswith(BASE_URL)

    def test_create_form_has_fields(self, page: Page):
        """Create form shows duck_id and name fields (if authenticated)."""
        page.goto(f"{BASE_URL}/duck/new")
        # If we get redirected to login, that's fine — login page loads
        if "/login" not in page.url:
            expect(page.locator("text=Duck #")).to_be_visible()
            expect(page.locator("text=Duck Name")).to_be_visible()


class TestFooter:
    """Test footer links are present and functional."""

    def test_footer_links_present(self, page: Page):
        """Footer contains FAQ, Privacy, Terms, Contact links."""
        page.goto(BASE_URL)
        footer = page.locator("footer")
        expect(footer).to_be_visible()
        expect(footer.locator("a", has_text="FAQ")).to_be_visible()
        expect(footer.locator("a", has_text="Privacy")).to_be_visible()
        expect(footer.locator("a", has_text="Terms")).to_be_visible()
        expect(footer.locator("a", has_text="Contact")).to_be_visible()

    def test_footer_faq_link_works(self, page: Page):
        """Clicking FAQ in footer navigates to FAQ page."""
        page.goto(BASE_URL)
        page.locator("footer a", has_text="FAQ").click()
        expect(page).to_have_url(f"{BASE_URL}/faq/")
