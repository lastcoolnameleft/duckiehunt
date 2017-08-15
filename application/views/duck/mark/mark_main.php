<?php
    echo form_open_multipart($controller, array('id' => 'form', 'name' => 'form'));
?>
<input type="hidden" name="duck_location_id" id="duck_location_id" value="<?php echo set_value('duck_location_id'); ?>" />
<input type="hidden" name="lat" id="lat" value="<?php echo set_value('lat', $lat); ?>" />
<input type="hidden" name="lng" id="lng" value="<?php echo set_value('lng', $lng); ?>" />

<div class="width25 floatLeft leftColumn">
	<div class='gradient'>
			<ol>
				<span><b>Instructions: </b></span>
				<li><span>Provide a Duck ID <font color='black'>*</font></span></li>
				<li><span>Enter a location and click Center <font color='black'>*</font></span></li>
				<li><span>Provide a Date / Time <font color='black'>*</font></span></li>
				<li><span>Click on the map to refine the marker</span></li>
				<li><span>Provide a Story/Link/Flickr Photo</span></li>
                <font color='black'>*</font> = Required
			</ol>
	</div>
</div>

<div class="width75 floatRight">
	<div class="gradient">
    <?php echo validation_errors('<div class="error">', '</div><br />'); ?>

<script src="/js/jquery-3.2.1.min.js" type="text/javascript" language="javascript"></script>

<script>
	function addInput( div, name, count, type, size) {
		if ( document.getElementById(count).value < 9) {
			document.getElementById(count).value = Number(document.getElementById(count).value) + 1;
			var d = document.createElement("div");
			var link = document.createElement("input");
			link.setAttribute("type", type);
			link.setAttribute('size', size);
			link.setAttribute("name", name + document.getElementById(count).value);
			d.appendChild(link);
			document.getElementById(div).appendChild(d);
		}
	}
</script>

<br/>
<table id='form_table'>
	<tr>
		<td valign='top'>
			<table>
				<tr><td>Duck: <font color='black'>*</font></td></tr>
				<tr><td><input type="text" name="duck_id" value="<?php echo set_value('duck_id', $duck_id); ?>" size="10" /></td></tr>

				<tr><td>Location: <font color='black'>*</font></td></tr>
				<tr><td><input type="text" name="location" id="location" value="<?php echo set_value('location', $location); ?>" size="30" /></td></tr>

				<tr><td>Date/Time: (MM/DD/YYYY HH:MM) <font color='black'>*</font></td></tr>
				<tr><td><input type="text" name="date_time" value="<?php echo set_value('date_time', $date_time); ?>" size="20" /></td></tr>

				<tr><td>Comment/Story:</td></tr>
				<tr><td><textarea name="comments" id="comments" rows="4" cols="28" size="20"><?php echo set_value('comments', $comments); ?></textarea></td></tr>

				<tr><td>Link:</td></tr>
				<tr><td>
                    <div id="linkDiv">
                    <?php
                        if (empty($links)) {
                            echo form_input(array('name' => 'link0', 'id' => 'link', 'size' => 30));
                        }
                        else {
                            for ($i=0; $i < sizeof($links); $i++) {
                                echo form_input(array('name' => 'link' . $i, 'id' => 'link' . $i, 'size' => 30, 'value' => set_value('link' . $i, $links[$i])));
                            }
                        }
                        ?>
                    </div>
                    <input type="hidden" value="<?php echo sizeof($links) ?>" id="link_id" />
                    <input type='button' onclick='addInput("linkDiv", "link", "link_id", "text", 30);' value='Add Another Link' />
                </td></tr>
                <tr><td>Upload Picture:</td></tr>
                <tr><td>
                    <input type="file" name="files[]" size="20" multiple />
                </td></tr>

				<tr><td><input type='submit' name="submit" value='Submit'></tr>
			</table>
		</td>
		<td width="75%">
				<div id="map"></div>
		</td>
	</tr>
</table>

	</div>
</div>

<?php echo form_close(); ?>

