<div id='map'></div>

<style>
 #map {
   width: 100%;
   height: 400px;
   background-color: grey;
   color: #000;
 }
</style>

<script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDQ9N94fMjCedY84yfdWjIw3uGIuOC8ymU&callback=initMap">
</script>

<script>
<?php
	echo "    var focus_lat={$focus_lat};\n";
	echo "    var focus_long={$focus_long};\n";
	echo "    var focus_zoom={$focus_zoom};\n";
	echo "    var duck_location_id={$duck_location_id};\n";
	echo "    var location_list=" . json_encode($location_list) . ";\n";
?>
	function initMap() {
		var map = new google.maps.Map(document.getElementById('map'), {
			zoom: focus_zoom,
			center: { lat: focus_lat, lng: focus_long }
		});
		var bounds = new google.maps.LatLngBounds();

		location_list.forEach((location, index) => {
			var position = new google.maps.LatLng( Number(location.latitude), Number(location.longitude) );
			var marker = new google.maps.Marker({ position: position, map: map, icon: '/images/icons/duck-32x32.png' });

			if (!(focus_lat && focus_long)) {
				bounds.extend(position);
			}
			var duck_header = '<a href="/view/duck/' + location.duck_id + '">Duck #' + location.duck_id + ' (' + location.name + ')</a>';
			var content = '<div id="content"><p>' + duck_header + '<br/>' + location.comments + '</p></div>';
			var infoWindow = new google.maps.InfoWindow( { content: content });
			marker.addListener('click', () => { infoWindow.open(map, marker); });
			if (location.duck_location_id == duck_location_id) {
				infoWindow.open(map, marker);
			}
		});

		if (!(focus_lat && focus_long)) {
			map.fitBounds(bounds);
		}

	}
</script>