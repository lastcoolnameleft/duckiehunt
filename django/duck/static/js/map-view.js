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
    var isDuckDetailPage = /\/duck\/\d+\/?$/.test(window.location.pathname);

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
        var pathSegments = [];
        var markerCount = 0;
        var activeInfoWindow = null;

        function openSingleInfoWindow(infoWindow, openOptions) {
            if (activeInfoWindow) {
                activeInfoWindow.close();
            }
            activeInfoWindow = infoWindow;
            infoWindow.open(openOptions);
        }

        map.addListener('click', function() {
            if (activeInfoWindow) {
                activeInfoWindow.close();
                activeInfoWindow = null;
            }
        });

        fetch(config.locationListApi)
            .then(function(response) { return response.json(); })
            .then(function(locationResult) {
                if (!Array.isArray(locationResult)) {
                    locationResult = [locationResult];
                }
                var validLocations = locationResult.filter(hasCoordinates);
                var groupedByDuck = groupLocationsByDuck(validLocations);

                validLocations.forEach(function(location) {
                    var position = new google.maps.LatLng(Number(location.latitude), Number(location.longitude));
                    var marker = new google.maps.Marker({ position: position, map: map, icon: duckIconUrl });
                    markerCount += 1;

                    if (!(config.focusLat && config.focusLong)) {
                        bounds.extend(position);
                    }

                    var content = buildSightingContent(location);
                    var infoWindow = new google.maps.InfoWindow({ content: content });
                    marker.addListener('click', function() {
                        openSingleInfoWindow(infoWindow, { map: map, anchor: marker });
                    });
                    if (Number(location.duck_location_id || location.pk) === Number(config.duckLocationId)) {
                        openSingleInfoWindow(infoWindow, { map: map, anchor: marker });
                    }
                });

                Object.keys(groupedByDuck).forEach(function(duckId) {
                    var sortedLocations = groupedByDuck[duckId].slice().sort(compareLocationsChronologically);
                    var strokeColor = getDuckColor(duckId);

                    for (var i = 1; i < sortedLocations.length; i += 1) {
                        var previous = sortedLocations[i - 1];
                        var current = sortedLocations[i];
                        var segmentPath = [
                            {
                                lat: Number(previous.latitude),
                                lng: Number(previous.longitude),
                            },
                            {
                                lat: Number(current.latitude),
                                lng: Number(current.longitude),
                            }
                        ];
                        var segment = new google.maps.Polyline({
                            path: segmentPath,
                            geodesic: false,
                            strokeColor: strokeColor,
                            strokeOpacity: 0.85,
                            strokeWeight: 3,
                            icons: [{
                                icon: getArrowSymbol(strokeColor),
                                offset: '0',
                                repeat: '120px',
                            }],
                            map: map,
                        });

                        segment.addListener('click', function(prevSighting, nextSighting) {
                            return function(event) {
                                var segmentInfo = new google.maps.InfoWindow({
                                    content: buildSegmentContent(prevSighting, nextSighting),
                                    position: event.latLng,
                                });
                                openSingleInfoWindow(segmentInfo, { map: map, position: event.latLng });
                            };
                        }(previous, current));

                        pathSegments.push(segment);
                    }
                });

                if (pathSegments.length > 0) {
                    addPathsToggleControl(map, pathSegments);
                }

                if (!(config.focusLat && config.focusLong) && markerCount > 0) {
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

    function hasCoordinates(location) {
        return location && location.latitude !== null && location.longitude !== null;
    }

    function groupLocationsByDuck(locations) {
        var grouped = {};
        locations.forEach(function(location) {
            var duckId = String(location.duck_id || 'unknown');
            if (!grouped[duckId]) {
                grouped[duckId] = [];
            }
            grouped[duckId].push(location);
        });
        return grouped;
    }

    function compareLocationsChronologically(left, right) {
        var leftTime = parseSightingTime(left);
        var rightTime = parseSightingTime(right);
        if (leftTime !== rightTime) {
            return leftTime - rightTime;
        }
        return Number(left.duck_location_id || left.pk || 0) - Number(right.duck_location_id || right.pk || 0);
    }

    function parseSightingTime(location) {
        var parsed = Date.parse(location.date_time);
        return Number.isNaN(parsed) ? 0 : parsed;
    }

    function buildSightingContent(location) {
        var duckName = location.duck__name ? ' (' + escapeHtml(location.duck__name) + ')' : '';
        var linkUrl = getSightingLink(location);
        var duckHeader = '<a href="' + escapeHtml(linkUrl) + '">Duck #' + escapeHtml(String(location.duck_id)) + duckName + '</a>';
        var photo = location.photo_thumbnail_url ? buildPopupImage(location.photo_thumbnail_url) : '';
        return '<div style="display:flex; gap:10px; align-items:flex-start; min-width: 240px; max-width: 340px;">'
            + photo
            + '<div style="flex:1; min-width: 0; line-height: 1.25;">'
            + '<div style="font-size: 14px; font-weight: 600; margin-bottom: 4px;">' + duckHeader + '</div>'
            + renderPopupRow('Location', location.location)
            + renderPopupRow('Seen', location.date_time ? formatDate(location.date_time) : '')
            + renderPopupRow('Notes', location.comments)
            + '</div>'
            + '</div>';
    }

    function getSightingLink(location) {
        if (isDuckDetailPage && location.duck_location_id) {
            return '/location/' + encodeURIComponent(location.duck_location_id);
        }
        return '/duck/' + encodeURIComponent(location.duck_id);
    }

    function buildSegmentContent(previous, current) {
        var duckName = current.duck__name ? ' (' + escapeHtml(current.duck__name) + ')' : '';
        var duckHeader = '<a href="/duck/' + encodeURIComponent(current.duck_id) + '">Duck #' + escapeHtml(String(current.duck_id)) + duckName + '</a>';
        return '<div style="min-width: 220px; max-width: 300px; line-height: 1.25;">'
            + '<div style="font-size: 14px; font-weight: 600; margin-bottom: 4px;">' + duckHeader + '</div>'
            + renderPopupRow('From', previous.location || 'Unknown')
            + renderPopupRow('Seen', previous.date_time ? formatDate(previous.date_time) : '')
            + renderPopupRow('To', current.location || 'Unknown')
            + renderPopupRow('Seen', current.date_time ? formatDate(current.date_time) : '')
            + '</div>';
    }

    function formatDate(value) {
        if (!value) {
            return 'Unknown';
        }
        var parsed = new Date(value);
        if (Number.isNaN(parsed.getTime())) {
            return String(value);
        }
        return parsed.toLocaleString();
    }

    function getDuckColor(duckId) {
        var hash = 0;
        var duckIdString = String(duckId);
        for (var i = 0; i < duckIdString.length; i += 1) {
            hash = ((hash << 5) - hash) + duckIdString.charCodeAt(i);
            hash |= 0;
        }
        var hue = Math.abs(hash) % 360;
        return 'hsl(' + hue + ', 75%, 45%)';
    }

    function renderPopupRow(label, value) {
        if (!value) {
            return '';
        }
        return '<div style="margin-bottom: 3px;">'
            + '<span style="color: #6c757d; font-size: 12px; display: block;">' + escapeHtml(label) + '</span>'
            + '<span style="font-size: 13px;">' + escapeHtml(String(value)) + '</span>'
            + '</div>';
    }

    function buildPopupImage(url) {
        return '<div style="flex:0 0 72px;">'
            + '<img src="' + escapeHtml(url) + '" alt="Duck photo" style="width:72px; height:72px; object-fit:cover; border-radius:8px; display:block;">'
            + '</div>';
    }

    function getArrowSymbol(color) {
        return {
            path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
            fillColor: color,
            fillOpacity: 1,
            strokeColor: color,
            strokeOpacity: 1,
            strokeWeight: 1,
            scale: 3,
        };
    }

    function addPathsToggleControl(map, pathSegments) {
        var controlDiv = document.createElement('div');
        controlDiv.style.background = '#fff';
        controlDiv.style.border = '2px solid #fff';
        controlDiv.style.borderRadius = '3px';
        controlDiv.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
        controlDiv.style.cursor = 'pointer';
        controlDiv.style.margin = '10px';
        controlDiv.style.padding = '6px 10px';
        controlDiv.style.fontSize = '14px';

        var label = document.createElement('label');
        label.style.margin = '0';
        label.style.display = 'flex';
        label.style.alignItems = 'center';
        label.style.gap = '6px';
        label.setAttribute('for', 'toggle-migration-paths');
        label.textContent = 'Show migration paths';

        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = 'toggle-migration-paths';
        checkbox.checked = true;
        checkbox.setAttribute('aria-label', 'Toggle migration paths');

        label.insertBefore(checkbox, label.firstChild);
        controlDiv.appendChild(label);

        checkbox.addEventListener('change', function() {
            pathSegments.forEach(function(segment) {
                segment.setMap(checkbox.checked ? map : null);
            });
        });

        map.controls[google.maps.ControlPosition.TOP_RIGHT].push(controlDiv);
    }

    initMap();
})();
