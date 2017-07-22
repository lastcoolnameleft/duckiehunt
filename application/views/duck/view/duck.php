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
				<?php echo (!empty($duck_info['comments']) ? "<tr><td>Comments</td><td>: {$duck_info['comments']}</td></tr>" : '')  ; ?>
			</table>
			<br/>

            Location History:
            <table>
<?php foreach ($duck_location_list as $duck_location) { ?>
                <ul style="margin-top: 3px; margin-bottom: 3px;">
                    <li><?php echo anchor( '/view/location/' . $duck_location['duck_location_id'], $duck_location['location']) ?></li>
                </ul>
<?php } ?>
            </table>
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

