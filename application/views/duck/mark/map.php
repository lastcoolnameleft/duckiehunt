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

	function initMap() {
		var map = new google.maps.Map(document.getElementById('map'), {
			zoom: 2,
			center: { lat: 37.92686760148135, lng: -94.921875 }
		});
	}
    function centerOnInput(center) {
        var location = center;
        var key = 'AIzaSyDXHyk9hmL302x8fjkpEbw5kVI0hjxsaos';
        var url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + location + '&key=' + key;
        $.get(url, (r) => { console.log(r) });
    }

</script>