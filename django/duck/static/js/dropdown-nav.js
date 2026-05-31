/**
 * Duck dropdown navigation for detail/location pages.
 *
 * Expected DOM elements:
 *   #duckDropdown - duck selector
 *   #locationDropdown - location selector (optional)
 */
document.addEventListener('DOMContentLoaded', function() {
    var duckDropdown = document.getElementById('duckDropdown');
    var locationDropdown = document.getElementById('locationDropdown');

    if (duckDropdown) {
        duckDropdown.addEventListener('change', function() {
            var duckId = this.options[this.selectedIndex].value;
            if (duckId) {
                window.location.href = '/duck/' + duckId;
            }
        });
    }

    if (locationDropdown) {
        locationDropdown.addEventListener('change', function() {
            var locationId = this.options[this.selectedIndex].value;
            if (locationId) {
                window.location.href = '/location/' + locationId;
            }
        });
    }
});
