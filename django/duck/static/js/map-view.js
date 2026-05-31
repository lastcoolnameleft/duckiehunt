/**
 * Duck detail/location map rendering.
 *
 * Expected globals (set by template):
 *   window.MAP_CONFIG = { focusLat, focusLong, focusZoom, duckLocationId, locationListApi }
 *   window.DUCK_ICON_URL
 *   window.GOOGLE_MAPS_API_KEY
 */
(function() {
    var config = window.MAP_CONFIG;
    var googleMapsApiKey = window.GOOGLE_MAPS_API_KEY;
    var duckIconUrl = window.DUCK_ICON_URL || '/static/icons/duck-32x32.png';

    if (!googleMapsApiKey) {
        console.warn('GOOGLE_MAPS_API_KEY is not configured.');
        return;
    }

    // Load Google Maps
    (function(g) {
        var h, a, k, p = "The Google Maps JavaScript API",
            c = "google", l = "importLibrary", q = "__ib__",
            m = document, b = window;
        b = b[c] || (b[c] = {});
        var d = b.maps || (b.maps = {}), r = new Set, e = new URLSearchParams,
            u = function() {
                return h || (h = new Promise(async function(f, n) {
                    await (a = m.createElement("script"));
                    e.set("libraries", [...r] + "");
                    for (k in g) e.set(k.replace(/[A-Z]/g, function(t) { return "_" + t[0].toLowerCase(); }), g[k]);
                    e.set("callback", c + ".maps." + q);
                    a.src = "https://maps." + c + "apis.com/maps/api/js?" + e;
                    d[q] = f;
                    a.onerror = function() { h = n(Error(p + " could not load.")); };
                    a.nonce = m.querySelector("script[nonce]")?.nonce || "";
                    m.head.append(a);
                }));
            };
        d[l] ? console.warn(p + " only loads once. Ignoring:", g) :
            d[l] = function(f) { r.add(f); return u().then(function() { return d[l](f); }); };
    })({
        key: googleMapsApiKey,
        v: "quarterly",
    });

    async function initMap() {
        var Map = (await google.maps.importLibrary("maps")).Map;

        var map = new Map(document.getElementById('map'), {
            zoom: config.focusZoom,
            center: { lat: config.focusLat, lng: config.focusLong }
        });
        var bounds = new google.maps.LatLngBounds();

        fetch(config.locationListApi)
            .then(function(response) { return response.json(); })
            .then(function(locationResult) {
                if (!Array.isArray(locationResult)) {
                    locationResult = [locationResult];
                }
                locationResult.forEach(function(location) {
                    var position = new google.maps.LatLng(Number(location.latitude), Number(location.longitude));
                    var marker = new google.maps.Marker({ position: position, map: map, icon: duckIconUrl });

                    if (!(config.focusLat && config.focusLong)) {
                        bounds.extend(position);
                    }

                    var duckName = location.duck__name ? ' (' + escapeHtml(location.duck__name) + ')' : '';
                    var duckHeader = '<a href="/duck/' + encodeURIComponent(location.duck_id) + '">Duck #' + escapeHtml(String(location.duck_id)) + duckName + '</a>';
                    var content = '<div id="content"><p>' + duckHeader + '<br/>' + escapeHtml(location.comments) + '</p></div>';
                    var infoWindow = new google.maps.InfoWindow({ content: content });
                    marker.addListener('click', function() { infoWindow.open(map, marker); });
                    if (location.pk == config.duckLocationId) {
                        infoWindow.open(map, marker);
                    }
                });

                if (!(config.focusLat && config.focusLong)) {
                    map.fitBounds(bounds);
                    map.setZoom(config.focusZoom);
                }
            })
            .catch(function(error) {
                console.error('Error fetching data:', error);
            });
    }

    function escapeHtml(str) {
        if (!str) return '';
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    initMap();
})();
