Welcome to DuckieHunt.com,<br/>
<br/>
Note:  Duckiehunt is currently experiencing technical difficulties.<br/> Please feel free to email me your locations/pictures at: <a href:"mailto:tommy@duckiehunt.com">tommy@duckiehunt.com</a><br/>
<br>
<br>
Don't know what you're doing here?  That's fine.  I'm not judging.  However, I'm willing to bet you fall into one of these categories.<br/>
<ul>
<li><?php echo anchor('/mark', 'You have a duck and want to mark it\'s location.') ?><br/>
<li><?php echo anchor('/view', 'You want to see a duck\'s migratory pattern.') ?><br/>
<li><?php echo anchor('/faq', 'You want some information on what the heck this is all about') ?><br/>
</ul>
I wish I was good with words.  But that's why I <?php echo anchor('http://flickr.com/photos/snoopykiss/2844038437', 'married') ?> an <?php echo anchor('http://flickr.com/photos/snoopykiss/tags/kathy', 'English Major') ?>.<br/>
<br/>
<br/>
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
	function initMap() {
		var uluru = {lat: 23, lng: 10};
		var map = new google.maps.Map(document.getElementById('map'), {
			zoom: 2,
			center: uluru
		});
<?php
		$point_array = array();

		if ( !empty($location_list) ) {
			foreach ( $location_list as $index => $location) {
				$latlong_name = "latlong_{$index}";
				$marker_name = "marker_{$index}";
				$infowindow_name = "infowindow_{$index}";

				echo "\tvar {$latlong_name} = { lat: {$location['latitude']}, lng: {$location['longitude']} };\n";
				echo "\tvar {$marker_name} = new google.maps.Marker({ position: {$latlong_name}, map: map, icon: '/images/icons/duck-32x32.png' });\n";
				if ( !empty($location['textbox']) ) {
					$textbox = '<div id="content"><p>';
					$textbox .= anchor('/view/duck/' . $location['duck_id'], "Duck #" . $location['duck_id'] . "<br/>");
					$comments = preg_replace("/\n/", '<br/>', $location['textbox']);
					$comments = (strlen($comments) > 30) ? substr($comments, 0, 30) . '...' : $comments;
					$textbox .= $comments;
					$textbox .= '</p></div>';
					echo "\tvar {$infowindow_name} = new google.maps.InfoWindow( { content: '{$textbox}' });\n";
					echo "\t{$marker_name}.addListener('click', function() { {$infowindow_name}.open(map, {$marker_name}); });\n";
				}
			}
		}
?>
	}
</script>