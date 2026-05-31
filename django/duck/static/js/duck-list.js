/**
 * Duck list search/filter functionality.
 *
 * Expected DOM elements:
 *   #duckSearch - search input
 *   .duck-card[data-search] - filterable cards
 *   #duckSearchEmpty - empty state message
 */
(function() {
    var searchInput = document.getElementById('duckSearch');
    var cards = document.querySelectorAll('.duck-card');
    var emptyState = document.getElementById('duckSearchEmpty');

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener('input', function(event) {
        var query = event.target.value.toLowerCase().trim();
        var visibleCount = 0;

        Array.prototype.forEach.call(cards, function(card) {
            var matches = card.getAttribute('data-search').indexOf(query) !== -1;
            card.style.display = matches ? '' : 'none';
            if (matches) {
                visibleCount += 1;
            }
        });

        emptyState.style.display = visibleCount ? 'none' : 'block';
    });
})();
