/**
 * Mark-a-duck form logic: duck name lookup, form submit spinner,
 * image compression, and Google Maps Places autocomplete integration.
 *
 * Expected DOM elements:
 *   #formMark, #buttonSubmit, #id_name, #id_duck_id, #name_notification,
 *   #map, #id_location, #id_lat, #id_lng, #id_image, #image_status
 *
 * Expected globals (set by template):
 *   window.GOOGLE_MAPS_API_KEY
 *   window.DUCK_ICON_URL
 */

var MAX_IMAGE_WIDTH = 1920;
var MAX_IMAGE_HEIGHT = 1920;
var IMAGE_QUALITY = 0.85;
var MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
var MAX_PHOTOS_PER_SIGHTING = 5;

/**
 * Compress an image file client-side before upload.
 * Returns a Promise that resolves to a compressed File, or the original if not an image.
 */
function compressImage(file) {
    return new Promise(function(resolve) {
        if (!file.type.startsWith('image/') || file.type === 'image/gif') {
            resolve(file);
            return;
        }

        var reader = new FileReader();
        reader.onload = function(e) {
            var img = new Image();
            img.onload = function() {
                var width = img.width;
                var height = img.height;

                // Only resize if larger than max dimensions
                if (width <= MAX_IMAGE_WIDTH && height <= MAX_IMAGE_HEIGHT && file.size <= 2 * 1024 * 1024) {
                    resolve(file);
                    return;
                }

                // Calculate new dimensions maintaining aspect ratio
                if (width > MAX_IMAGE_WIDTH) {
                    height = Math.round(height * MAX_IMAGE_WIDTH / width);
                    width = MAX_IMAGE_WIDTH;
                }
                if (height > MAX_IMAGE_HEIGHT) {
                    width = Math.round(width * MAX_IMAGE_HEIGHT / height);
                    height = MAX_IMAGE_HEIGHT;
                }

                var canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob(function(blob) {
                    var compressed = new File([blob], file.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    resolve(compressed);
                }, 'image/jpeg', IMAGE_QUALITY);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('formMark');
    var submitBtn = document.getElementById('buttonSubmit');
    var nameField = document.getElementById('id_name');
    var duckIdField = document.getElementById('id_duck_id');
    var nameNotification = document.getElementById('name_notification');
    var imageInput = document.getElementById('id_image');
    var imageStatus = document.getElementById('image_status');
    var imagePreviewGrid = document.getElementById('image_preview_grid');
    var imageDropZone = document.getElementById('image_drop_zone');

    // Default date/time to the user's local "now" if empty
    var dateTimeField = document.getElementById('id_date_time');
    if (dateTimeField && !dateTimeField.value) {
        var now = new Date();
        var local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
        dateTimeField.value = local.toISOString().slice(0, 16);
    }

    function setImageStatus(message, className) {
        if (!imageStatus) return;
        imageStatus.textContent = message || '';
        imageStatus.className = 'form-text' + (className ? ' ' + className : '');
    }

    function clearPreviews() {
        if (imagePreviewGrid) {
            imagePreviewGrid.innerHTML = '';
        }
    }

    function renderPreviews(files) {
        if (!imagePreviewGrid) return;
        clearPreviews();
        files.forEach(function(file) {
            if (!file || !file.type.startsWith('image/')) return;

            var wrapper = document.createElement('div');
            wrapper.className = 'mr-2 mb-2 text-center';

            var image = document.createElement('img');
            image.className = 'border rounded';
            image.style.width = '120px';
            image.style.height = '120px';
            image.style.objectFit = 'cover';
            image.alt = file.name;

            var label = document.createElement('div');
            label.className = 'small text-muted mt-1';
            label.textContent = file.name;

            var url = window.URL.createObjectURL(file);
            image.onload = function() {
                window.URL.revokeObjectURL(url);
            };
            image.src = url;

            wrapper.appendChild(image);
            wrapper.appendChild(label);
            imagePreviewGrid.appendChild(wrapper);
        });
    }

    function replaceInputFiles(files) {
        if (!imageInput || typeof DataTransfer === 'undefined') return;
        var dt = new DataTransfer();
        files.forEach(function(file) {
            dt.items.add(file);
        });
        imageInput.files = dt.files;
    }

    function getFiles(fileList) {
        return Array.prototype.slice.call(fileList || []);
    }

    function clearImageSelection(keepStatus) {
        if (imageInput) {
            imageInput.value = '';
        }
        clearPreviews();
        if (!keepStatus) {
            setImageStatus('');
        }
    }

    function validateFiles(files) {
        if (files.length > MAX_PHOTOS_PER_SIGHTING) {
            setImageStatus('You can upload at most ' + MAX_PHOTOS_PER_SIGHTING + ' photos per sighting.', 'text-danger');
            clearImageSelection(true);
            return false;
        }

        for (var i = 0; i < files.length; i += 1) {
            if (files[i].size > MAX_FILE_SIZE) {
                setImageStatus('File is too large (max 10MB). Please choose a smaller image.', 'text-danger');
                clearImageSelection(true);
                return false;
            }
        }

        return true;
    }

    function handleImageSelection(fileList) {
        var files = getFiles(fileList);
        if (!files.length) {
            clearImageSelection();
            return;
        }

        if (!validateFiles(files)) {
            return;
        }

        var needsCompression = files.some(function(file) {
            return file.type.startsWith('image/') && file.size > 2 * 1024 * 1024;
        });

        if (needsCompression) {
            setImageStatus('Compressing images...', 'text-muted');
        } else {
            setImageStatus(files.length + ' photo' + (files.length === 1 ? '' : 's') + ' selected', 'text-muted');
        }

        Promise.all(files.map(compressImage)).then(function(compressedFiles) {
            if (!validateFiles(compressedFiles)) {
                return;
            }

            replaceInputFiles(compressedFiles);
            renderPreviews(compressedFiles);
            setImageStatus(compressedFiles.length + ' photo' + (compressedFiles.length === 1 ? '' : 's') + ' ready', 'text-success');
        });
    }

    // Client-side image compression on file select / drop
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            handleImageSelection(imageInput.files);
        });
    }

    if (imageDropZone && imageInput) {
        imageDropZone.addEventListener('dragover', function(event) {
            event.preventDefault();
            imageDropZone.classList.add('border-primary');
        });

        imageDropZone.addEventListener('dragleave', function() {
            imageDropZone.classList.remove('border-primary');
        });

        imageDropZone.addEventListener('drop', function(event) {
            event.preventDefault();
            imageDropZone.classList.remove('border-primary');
            if (event.dataTransfer && event.dataTransfer.files) {
                handleImageSelection(event.dataTransfer.files);
            }
        });
    }

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

    // "Use my location" button — browser geolocation
    var locationBtn = document.getElementById('btnUseMyLocation');
    var locationStatus = document.getElementById('location_status');

    if (locationBtn && navigator.geolocation) {
        locationBtn.addEventListener('click', function() {
            locationBtn.disabled = true;
            locationBtn.textContent = 'Getting location...';
            locationStatus.textContent = '';

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    var lat = position.coords.latitude;
                    var lng = position.coords.longitude;

                    document.getElementById('id_lat').value = lat;
                    document.getElementById('id_lng').value = lng;

                    var latlng = new google.maps.LatLng(lat, lng);
                    map.setCenter(latlng);
                    map.setZoom(15);
                    marker.setPosition(latlng);
                    marker.setVisible(true);

                    // Reverse geocode to get a readable address
                    var geocoder = new google.maps.Geocoder();
                    geocoder.geocode({ location: latlng }, function(results, status) {
                        if (status === 'OK' && results[0]) {
                            input.value = results[0].formatted_address;
                            locationStatus.textContent = 'Location set from your device';
                            locationStatus.className = 'form-text text-success';
                        } else {
                            input.value = lat.toFixed(4) + ', ' + lng.toFixed(4);
                            locationStatus.textContent = 'Coordinates set (could not resolve address)';
                            locationStatus.className = 'form-text text-success';
                        }
                        locationBtn.disabled = false;
                        locationBtn.textContent = 'Use my location';
                    });
                },
                function(error) {
                    locationBtn.disabled = false;
                    locationBtn.textContent = 'Use my location';
                    var msg = 'Unable to get location. ';
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            msg += 'Permission denied — you can type a location instead.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            msg += 'Position unavailable — try again or type a location.';
                            break;
                        case error.TIMEOUT:
                            msg += 'Request timed out — try again.';
                            break;
                    }
                    locationStatus.textContent = msg;
                    locationStatus.className = 'form-text text-danger';
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
            );
        });
    } else if (locationBtn) {
        // Browser doesn't support geolocation
        locationBtn.style.display = 'none';
    }
}
