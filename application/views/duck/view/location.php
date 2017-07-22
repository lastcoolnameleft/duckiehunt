<table>
	<tr valign='top'>
		<td>
<?php	if (!empty($duck_id) && !empty($duck_info)) { ?>
			<table>
				<tr><td>Duck ID</td><td>:</td><td><?php echo $duck_id ?></td></tr>
				<tr><td>Name</td><td>:</td><td><?php echo empty($duck_info['name']) ? 'Unnamed' : $duck_info['name'] ?></td></tr>
				<tr><td>Total Distance Travelled</td><td>:</td><td><?php echo $duck_info['total_distance'] ?> Miles</td></tr>
<?php 
                 if (!empty($duck_info['comments'])) {
                    echo "<tr><td>Comments</td><td>:</td><td>{$duck_info['comments']}</td></tr>";
                 }
                 if (!empty($location_info)) {
                     echo "<tr><td colspan='3'><h2>Location Info</h2></td></tr>";
                     echo "<tr><td>Location</td><td>:</td><td>{$location_info['location']}</td></tr>";
                     echo "<tr><td>Date/Time</td><td>:</td><td>{$location_info['date_time']}</td></tr>";
                     if (!empty($location_info['user_id'])) {
                        echo "<tr><td>User</td><td>:</td><td>{$location_info['username']}</td></tr>";
                     }
                     if (!empty($location_info['comments'])) {
                        echo "<tr><td>Comments</td><td>:</td><td>{$location_info['comments']}</td></tr>";
                     }
                     if (!empty($location_info['flickr_photo_info']['page'])) {
                         echo "<tr><td>Flickr Page</td><td>:</td><td>" . anchor($location_info['flickr_photo_info']['page'], $location_info['flickr_photo_info']['title']) . "</td></tr>";
                     }
                     if (!empty($location_info['distance_to'])) {
                        echo "<tr><td>Distance To this Point</td><td>:</td><td>{$location_info['distance_to']}</td></tr>";
                     }
                     echo "<tr><td>Longitude</td><td>:</td><td>{$location_info['longitude']}</td></tr>";
                     echo "<tr><td>Latitude</td><td>:</td><td>{$location_info['latitude']}</td></tr>";
                     if (!empty($links)) {
                         echo "<tr><td>Link(s)</td><td>:</td><td>";
                         foreach ($links as $link) {
                             echo anchor($link) . "<br />";
                         }
                         echo  "</td></tr>";
                     }

                 }
?>
			</table>
			<br/>
<?php
	}

    if ( $can_modify ) {
		echo "Modify Duck Location: ";
        echo "<input type='button' name='edit_loc' onClick='document.location=\"/mark/update/{$duck_location_id}\"' value='Edit Location' />";
    }
    
	if (!empty($duck_id)) {
        echo "<table>\n";
		$this->load->helper('form');
		if ($is_tracking) {
            echo "<tr><td>\n";
			echo form_open('view/alert/' . $duck_id . '/remove');
			echo "Stop alerts for this duck<br/>";
			echo '</td><td>' . form_submit('remove_alert', 'Release me!') . '</td></tr>';
            echo form_close();
		}
		else {
            echo "<tr><td>\n";
			echo form_open('view/add_alert');
			echo form_hidden('duck_id', $duck_id);
			echo "Get alerts for this duck: ";
			echo '</td><td>' . form_submit('add_alert', 'Alert me!') . '</td></tr>';
            echo form_close();
//			echo "<font color='black'>Requires valid login</font>";
		}
        echo "</table>\n";
	} 
	?>
		</td>
		<td>
			<div id="map"></div>
		</td>

	</tr>
</table>
