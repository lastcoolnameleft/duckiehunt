/**
 * Mark-a-duck form logic: duck name lookup, form submit spinner,
 * and Google Maps Places autocomplete integration.
 *
 * Expected DOM elements:
 *   #formMark, #buttonSubmit, #id_name, #id_duck_id, #name_notification,
 *   #map, #id_location, #id_lat, #id_lng
 *
 * Expected globals (set by template):
 *   window.GOOGLE_MAPS_API_KEY
 *   window.DUCK_ICON_URL
 */
document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('formMark');
    var submitBtn = document.getElementById('buttonSubmit');
    var nameField = document.getElementById('id_name');
    var duckIdField = document.getElementById('id_duck_id');
    var nameNotification = document.getElementById('name_notification');

    form.addEventListener('submit', function() {
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        submitBtn.disabled = true;
    });

    nameField.disabled = true;

    duckIdField.addEventListener('blur', checkDuckName);

    function checkDuckName() {
        var duck_id = duckIdField.value;
        if (!parseInt(duck_id) || 1 >= parseInt(duck_id)) {
            return;
        }
        var get_duck_url = '/api/duck/' + duck_id;
        fetch(get_duck_url)
            .then(function(response) {
                if (!response.ok) {
                    if (response.status === 404) {
                        enableDuckName();
                    }
                    throw new Error('Not found');
                }
                return response.json();
            })
            .then(function(result) {
                var duck_name = result.name;
                if (!duck_name || duck_name === 'Undefined' || duck_name === 'Unnamed') {
                    enableDuckName();
                } else {
                    disableDuckName(duck_name);
                }
            })
            .catch(function() {});
    }

    function enableDuckName() {
        nameField.disabled = false;
        nameField.value = '';
        nameNotification.textContent = 'This Duck does not have a name yet! Please be creative, not dirty.';
    }

    function disableDuckName(duck_name) {
        nameField.disabled = true;
        nameField.value = duck_name;
        nameNotification.textContent = '';
    }

    checkDuckName();
});

function initMap() {
    var duckIconUrl = window.DUCK_ICON_URL || '/static/icons/duck-32x32.png';
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 1,
        center: { lat: 35, lng: -30 }
    });

    var input = document.getElementById('id_location');
    var autocomplete = new google.maps.places.Autocomplete(input, {
        fields: ['geometry', 'formatted_address', 'name'],
    });
    autocomplete.bindTo('bounds', map);
    var marker = new google.maps.Marker({ map: map, icon: duckIconUrl });
    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });
    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            window.alert("No details available for input: '" + place.name + "'");
            return;
        }

        document.getElementById('id_lat').value = place.geometry.location.lat();
        document.getElementById('id_lng').value = place.geometry.location.lng();

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);
        }

        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
    });
}
