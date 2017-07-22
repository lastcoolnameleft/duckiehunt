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
	echo "var focus_lat={$focus_lat};\n";
	echo "var focus_long={$focus_long};\n";
	echo "var focus_zoom={$focus_zoom};\n";
	echo "var location_list=" . json_encode($location_list) . ";\n";
?>
	function initMap() {
		var map = new google.maps.Map(document.getElementById('map'), {
			zoom: focus_zoom,
			center: {lat: focus_lat, lng: focus_long}
		});
		location_list.forEach((location, index) => {
			var position = { lat: Number(location.latitude), lng: Number(location.longitude) };
			var marker = new google.maps.Marker({ position: position, map: map, icon: '/images/icons/duck-32x32.png' });
			var duck_header = '<a href="/view/duck/' + location.duck_id + '">Duck #' + location.duck_id + '</a>';
			var content = '<div id="content"><p>' + duck_header + '<br/>' + location.comments + '</p></div>';
			var infoWindow = new google.maps.InfoWindow( { content: content });
			marker.addListener('click', function() { infoWindow.open(map, marker); });
		});

	}
</script>