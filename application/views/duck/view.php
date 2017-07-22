<?php /**/ ?><?php
  $start_lat = 37.4041960114344;
  $start_lon = -122.008194923401;
  $zoom = 9;
  $app_id = 's2lBliLV34ETsPKJ1Z4g1wFkjxga.u7iSIZHQmIGz8d3U3BTIiHDhq.WtmddJbf6NT1vJ1fAjA--';
?>

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


<table>
		<tr>
<?php echo (!empty($user_duck_list)) ? '<td>Tracked Ducks:</td>' : ''; ?>
			<td>All Ducks:</td>
		</tr>
		<tr>
<?php echo (!empty($user_duck_list)) ? '<td>' . form_dropdown('user_duck_id', $user_duck_list, $duck_id, 'onChange="javascript:formHandler(this)"' ) . '</td>' : ''; ?>
			<td><?php echo form_dropdown('total_duck_id', $total_duck_list, $duck_id, 'onChange="javascript:formHandler(this)"' ); ?></td></tr>
</table>
<table>
	<tr valign='top'>
		<td>
			<div id="map"></div>
		</td>
		<td>
<?php	if (!empty($duck_id) && !empty($duck_info)) { ?>
			<table>
				<tr><td>Name</td><td>: <?php echo $duck_info['name'] ?></td></tr>
				<tr><td>Distance Travelled</td><td>: <?php echo $duck_info['total_distance'] ?> Miles</td></tr>
				<tr><td>Comments</td><td>: <?php echo $duck_info['comments'] ?></td></tr>
			</table>
			<br/>
<?php
	}
	if (!empty($duck_id)) {
		$this->load->helper('form');
		if ($is_tracking) {
			echo form_open('view/alert/' . $duck_id . '/remove');
			echo "Stop alerts for this duck<br/>";
			echo form_submit('mysubmit', 'Release me!') . '<br/>';
		}
		else {
			echo form_open('view/add_alert');
			echo form_hidden('duck_id', $duck_id);
			echo "Get alerts for this duck: ";
			echo form_submit('mysubmit', 'Alert me!') . '<br/>';
//			echo "<font color='black'>Requires valid login</font>";
		}
		echo form_close();
	} 
	?>
		</td>
	</tr>
</table>
    <script type="text/javascript" src="http://api.maps.yahoo.com/ajaxymap?v=3.8&appid=<?php echo $app_id ?>"></script>
        <script type="text/javascript" language="JavaScript">
function formHandler(obj)
{
	var duck_id = obj[obj.selectedIndex].value;
	var URL = '<?php echo $base_url; ?>view/duck/' + duck_id;
	window.location.href = URL;
}

        YLog.initSize(new YSize(600,300));
        function StartYMap() {
                var map = new YMap(document.getElementById('map'),YAHOO_MAP_REG); 
                var cPT = new YGeoPoint(<?php echo $start_lat ?>, <?php echo $start_lon ?>);
                map.drawZoomAndCenter(cPT,<?php echo $zoom ?>);

                map.addTypeControl();
                map.addZoomLong();
                map.addPanControl();
				
<?php     
		$point_array = array();

		if ( !empty($duck_location) ) {
			foreach ( $duck_location as $index => $location) {
				$js_point_name = "cPT{$index}";

				$marker_name = "marker{$index}";
				echo "\t\tvar {$js_point_name} = new YGeoPoint( {$location['latitude']}, {$location['longitude']} );\n";
				echo "\t\tvar {$marker_name} = new YMarker({$js_point_name}, null, '{$marker_name}');\n";
				echo "\t\tvar new_image = new YImage();\n";
				echo "\t\tnew_image.src = '/duck-16x16.png'\n";
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
            echo "\t\tmap.drawZoomAndCenter(zoomcenter.YGeoPoint, zoomcenter.zoomLevel );\n";

		}
?>
        }
        window.onload = StartYMap;
        </script>


