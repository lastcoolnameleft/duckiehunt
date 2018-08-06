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
#                     if (!empty($location_info['user_id'])) {
#                        echo "<tr><td>User</td><td>:</td><td>{$location_info['username']}</td></tr>";
#                     }
                     if (!empty($location_info['comments'])) {
                        echo "<tr><td>Comments</td><td>:</td><td>{$location_info['comments']}</td></tr>";
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
                     if (!empty($photos)) {
                         echo "<tr><td>Photos</td><td>:</td><td>\n";
                         foreach ($photos as $photo_id => $thumbnail_url) {
                            echo '<a data-flickr-embed="true"  href="https://www.flickr.com/photos/duckiehunt/' . $photo_id . '/" title="Duck #' . $duck_id . '"><img src="' . $thumbnail_url . '" alt="Duck #' . $duck_id . '"></a><script async src="//embedr.flickr.com/assets/client-code.js" charset="utf-8"></script>';
//                            echo "<a href='https://www.flickr.com/photos/duckiehunt/{$photo_id}/'><img src='{$thumbnail_url}' /></a></td></tr>";
                         }
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
	?>
		</td>
		<td>
		</td>

	</tr>
</table>
