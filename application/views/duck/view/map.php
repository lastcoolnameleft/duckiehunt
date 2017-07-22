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
</style>

<script type="text/javascript" src="http://api.maps.yahoo.com/ajaxymap?v=3.8&appid=<?php echo $this->config->item('y_app_id'); ?>"></script>
<script type="text/javascript" language="JavaScript">
var map;
function redirectToDuck(obj)
{
	var duck_id = obj[obj.selectedIndex].value;
	var URL = '/view/duck/' + duck_id;
	window.location.href = URL;
}

function redirectToDuckLocation(obj)
{
	var location_id = obj[obj.selectedIndex].value;
	var URL = '/view/location/' + location_id;
	window.location.href = URL;
}

//        YLog.initSize(new YSize(600,300));
        function StartYMap() {
                map = new YMap(document.getElementById('map'),YAHOO_MAP_REG);
                var cPT = new YGeoPoint(<?php echo $this->config->item('start_lat'); ?>, <?php echo $this->config->item('start_lon'); ?>);
                map.drawZoomAndCenter(cPT,<?php echo $this->config->item('start_zoom'); ?>);
                map.addTypeControl();
                map.addZoomLong();
                map.addPanControl();

<?php
		$point_array = array();

		if ( !empty($location_list) ) {
			foreach ( $location_list as $index => $location) {
				$js_point_name = "cPT{$index}";

				$marker_name = "marker{$index}";
				echo "\t\tvar {$js_point_name} = new YGeoPoint( {$location['latitude']}, {$location['longitude']} );\n";
				echo "\t\tvar {$marker_name} = new YMarker({$js_point_name}, null, '{$marker_name}');\n";
				echo "\t\tvar new_image = new YImage();\n";
//				echo "\t\tnew_image.src = '" . (empty($location['thumbnail_url']) ? '/duck-16x16.png' : $location['thumbnail_url']) . "'\n";
				echo "\t\tnew_image.src = '/images/icons/duck-32x32.png'\n";
				echo "\t\t{$marker_name}.changeImage(new_image);\n";

				if ( !empty($location['textbox']) ) {
					$textbox = preg_replace("/\n/", '<br/>', $location['textbox']);
//					$textbox = preg_replace('@(https?://([-\w\.]+)+(:\d+)?(/([\w/_\.#]*(\?\S+)?)?)?)@', '<a href="$1">$1</a>', $textbox);
					echo "\t\tYEvent.Capture({$marker_name}, EventsList.MouseClick, function(){ {$marker_name}.openSmartWindow('<div>{$textbox}</div>');  });\n";
				}

				echo "\t\tmap.addOverlay({$marker_name});\n\n\n";
				$point_array[] = $js_point_name;
			}
                // args: array of pts, color, width, alpha
			echo "\t\tvar poly1 = new YPolyline([" . implode(',', $point_array) . "],'blue',7,0.7);\n";
			echo "\t\tmap.addOverlay(poly1);\n\n";
			echo "\t\tvar zoomcenter = map.getBestZoomAndCenter([" . implode(',', $point_array) . "]);\n\n";
            echo "\t\tzoomcenter.zoomLevel = (zoomcenter.zoomLevel >= 18) ? 17 : zoomcenter.zoomLevel\n";
            echo "\t\tmap.drawZoomAndCenter(zoomcenter.YGeoPoint, zoomcenter.zoomLevel );\n";

		}
?>
        }
        window.onload = StartYMap;
        </script>

