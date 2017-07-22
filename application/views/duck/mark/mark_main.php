<?php
    echo form_open_multipart($controller, array('id' => 'form', 'name' => 'form', 'onSubmit' => 'return validateData();'));
    echo form_hidden('lat', '');
    echo form_hidden('lon', '');
    echo (!empty($duck_location_id)) ? form_hidden('duck_location_id', $duck_location_id) : '';
?>

<div class="width25 floatLeft leftColumn">
	<div class='gradient'>
			<ol>
				<li><span>Provide a Duck ID <font color='black'>*</font></span></li>
				<li><span>Provide a Date / Time <font color='black'>*</font></span></li>
				<li><span>Enter a location and click Center <font color='black'>*</font></span></li>
				<li><span>Click on the map to refine the marker</span></li>
				<li><span>Provide a Story/Link/Flickr Photo</span></li>
                <font color='black'>*</font> = Required
			</ol>
	</div>
</div>

<div class="width75 floatRight">
	<div class="gradient">
    <?php echo validation_errors('<div class="error">', '</div><br />'); ?>

<!-- Dependency -->
<script src="http://yui.yahooapis.com/2.5.2/build/yahoo/yahoo-min.js"></script>

<!-- Used for Custom Events and event listener bindings -->
<script src="http://yui.yahooapis.com/2.5.2/build/event/event-min.js"></script>

<!-- Source file -->
<script src="http://yui.yahooapis.com/2.5.2/build/connection/connection-min.js"></script>
<script src="/js/jquery-1.2.6.js" type="text/javascript" language="javascript"></script>
<script src="/js/jquery.MultiFile.min.js" type="text/javascript" language="javascript"></script>


<style type="text/css">
#yswid{
color: #000000;
}
#ymaplog{
color: #888888;
}
</style>
   
<br/>
<table>
	<tr>
		<td valign='top'>
			<table>
				<tr><td>Duck: <font color='black'>* <?php //echo $this->form_validation->duck_id_error; ?></font></td></tr>
				<tr><td><?php echo form_input('duck_id', set_value('duck_id', $location_info['duck_id']) ) ?></td></tr>
				<tr><td>Location: <font color='black'>* <?php //echo $this->form_validation->duck_id_error; ?></font></td></tr>
				<tr><td>
                    <?php echo form_input(array('name' => 'center', 'id' => 'center', 'size' => 20, 'value' => set_value('location', $location_info['location']))) ?>
                    <input type='button' onClick='centerOnInput(document.getElementById("center").value);' value='Center'/>
                    <font color='black'>*</font>
				</td></tr>
				<tr><td>Date/Time: (MM/DD/YYYY HH:MM) <font color='black'>*</font></td></tr>
				<tr><td><?php echo form_input('date_time', set_value('date_time', $location_info['date_time'])); ?></td></tr>
				<tr><td>Comment/Story:</td></tr>
				<tr><td><?php echo form_textarea( array('name' => 'comments', 'id' => 'comments', 'rows' => 4, 'cols' => 28, 'value' => set_value('comments', $location_info['comments']))) ?></td></tr>
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
                    <input type="hidden" value="0" id="link_id" />
                    <input type='button' onclick='addInput("linkDiv", "link", "link_id", "text", 30);' value='Add Another Link' />

                </td></tr>
                <tr><td>Upload Picture(s):</td></tr>
                <tr><td>
                    <input type="file" name="userfile[]" size="20" class="multi" />
                </td></tr>
                <!--<tr><td>Flickr Photo ID:</td></tr>
				<tr><td><?php echo form_input(array('name' => 'flickr_photo_id', 'id' => 'flickr_photo_id', 'size' => 15, 'value' => set_value('flickr_photo_id', $location_info['flickr_photo_id']))) ?></td></tr> -->
				<tr><td><input type='submit' value='Submit'></tr>
			</table>
		<td valign='top'>
			<table>
				<tr><td>
				<div id="map"></div></td></tr>
			</table>
		</td>
	</tr>
</table>

	</div>
</div>

<?php echo form_close(); ?>

