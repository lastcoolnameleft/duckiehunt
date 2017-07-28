<style>
 #map {
   width: 100%;
   height: 400px;
   background-color: grey;
   color: #000;
 }
</style>

<script>
	function initMap() {
		var map = new google.maps.Map(document.getElementById('map'), {
			zoom: 1,
			center: { lat: 35, lng: -30 }
		});

        // Map auto-center and focus on location
        $( '#location' ).focusout(() => {
            console.log('fetching location');
            var location = $('#location').get(0).value;
            var key = 'AIzaSyDXHyk9hmL302x8fjkpEbw5kVI0hjxsaos';
            var url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + location + '&key=' + key;
            $.get(url, (result) => {
                if (result.results.length === 0 || result.status !== "OK") {
                    alert('Invalid location.  Please try again.');
                } else {
                    var position = {
                        lat: result.results[0].geometry.location.lat,
                        lng: result.results[0].geometry.location.lng
                    };
                    $('#lat')[0].value = position.lat;
                    $('#lng')[0].value = position.lng;

                    map.setCenter(position);
                    map.setZoom(7);
                    var marker = new google.maps.Marker({ position: position, map: map, icon: '/images/icons/duck-32x32.png' });
                }
            });
        });

	}

</script>

<script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDXHyk9hmL302x8fjkpEbw5kVI0hjxsaos&callback=initMap">
</script>
