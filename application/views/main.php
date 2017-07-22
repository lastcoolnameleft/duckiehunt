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

<style type="text/css">
#map a:hover {
    color:black;
}

#map div {
    color: black;
font: 100 0.9em "trebuchet ms", serif;

}

td.text {
	color:blue;
}

#map{
  height: 55%;
  width: 60%;
}
</style>
</style>



<script type="text/javascript" src="http://api.maps.yahoo.com/ajaxymap?v=3.8&appid=<?php echo $this->config->item('y_app_id'); ?>"></script>
<script type="text/javascript" language="JavaScript">
var map;

function StartYMap() {
    map = new YMap(document.getElementById('map'),YAHOO_MAP_REG);
    var cPT = new YGeoPoint(<?php echo $this->config->item('start_lat'); ?>, <?php echo $this->config->item('start_lon'); ?>);
    map.drawZoomAndCenter(cPT,<?php echo $this->config->item('start_zoom'); ?>);
    map.addTypeControl();
    map.addZoomLong();
    map.addPanControl();
//	map.disableDragMap();

<?php
		$point_array = array();

		if ( !empty($location_list) ) {
			foreach ( $location_list as $index => $location) {
				$js_point_name = "cPT{$index}";

				$marker_name = "marker{$index}";
				echo "\tvar {$js_point_name} = new YGeoPoint( {$location['latitude']}, {$location['longitude']} );\n";
				echo "\tvar {$marker_name} = new YMarker({$js_point_name}, null, '{$marker_name}');\n";
				echo "\tvar new_image = new YImage();\n";
				echo "\tnew_image.src = '/images/icons/duck-32x32.png'\n";
				echo "\t{$marker_name}.changeImage(new_image);\n";

				if ( !empty($location['textbox']) ) {
					$textbox = anchor('/view/duck/' . $location['duck_id'], "Duck #" . $location['duck_id'] . "<br/>");
					$comments = preg_replace("/\n/", '<br/>', $location['textbox']);
					$comments = (strlen($comments) > 30) ? substr($comments, 0, 30) . '...' : $comments;
					$textbox .= $comments;
					echo "\tYEvent.Capture({$marker_name}, EventsList.MouseOver, function(){ {$marker_name}.openSmartWindow('<div>{$textbox}</div>');  });\n";
				}

				echo "\tmap.addOverlay({$marker_name});\n\n\n";
				$point_array[] = $js_point_name;
			}

            echo "\tvar zoomcenter = map.getBestZoomAndCenter([" . implode(',', $point_array) . "]);\n\n";
            echo "\tzoomcenter.zoomLevel = (zoomcenter.zoomLevel >= 18) ? 17 : zoomcenter.zoomLevel\n";
            echo "\tmap.drawZoomAndCenter(zoomcenter.YGeoPoint, zoomcenter.zoomLevel );\n";

		}
?>
}
window.onload = StartYMap;
</script>

