<!-- Page Content -->
<div class="container">

	<!-- Page Heading/Breadcrumbs -->
	<h1 class="mt-4 mb-3">Mark a Duck</h1>

	<ol class="breadcrumb">
		<li class="breadcrumb-item">
			<a href="/">Home</a>
		</li>
		<li class='breadcrumb-item active'>Mark a duck</li>
	</ol>

	<!--
	<div class="row">
		<div class="col-lg-6">
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
-->
	<div class="row">
		<div class="col-lg-12">
			<?php echo validation_errors('<div class="error">', '</div><br />'); ?>
			<form action="/mark" id="form" name="form" enctype="multipart/form-data" method="post" accept-charset="utf-8">
			<input type="hidden" name="duck_location_id" id="duck_location_id" value="<?php echo set_value('duck_location_id'); ?>" />
			<input type="hidden" name="lat" id="lat" value="<?php echo set_value('lat', $lat); ?>" />
			<input type="hidden" name="lng" id="lng" value="<?php echo set_value('lng', $lng); ?>" />
			<dl class="row">
				<dt class="col-sm-4">Duck #:</dt>
				<dd class="col-sm-8"><input type="text" name="duck_id" value="<?php echo set_value('duck_id', $duck_id); ?>" size="10" /></dd>
				<dt class="col-sm-4">Location: (e.g. Eiffel Tower)</dt>
				<dd class="col-sm-8"><input type="text" name="location" id="location" value="<?php echo set_value('location', $location); ?>" size="30" /></dd>
				<dt class="col-sm-4">Map:</dt>
				<dd class="col-sm-8"><div id="map"></div></dd>
				<dt class="col-sm-4">Date/Time: (e.g. MM/DD/YYYY HH:MM)</dt>
				<dd class="col-sm-8"><input type="text" name="date_time" value="<?php echo set_value('date_time', $date_time); ?>" size="20" /></dd>
				<dt class="col-sm-4">Comment/Story:</dt>
				<dd class="col-sm-8"><textarea name="comments" id="comments" rows="6" cols="50" size="20"><?php echo set_value('comments', $comments); ?></textarea></dd>
				<dt class="col-sm-4">Link:</dt>
				<dd class="col-sm-8">
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
				</dd>
				<dt class="col-sm-4">Upload Picture:</dt>
				<dd class="col-sm-8"><input type="file" name="files[]" size="20" multiple /></dd>
				<dt class="col-sm-4">&nbsp;</dt>
				<dt class="col-sm-8"><?php echo $recaptcha_widget ?></dt>
				<dt class="col-sm-4">&nbsp;</dt>
				<dd class="col-sm-8"><input type='submit' name="submit" value='Submit the new location'></dd>
			</dl>
			</form>
		</div>
	</div>
</div>

<?php echo $recaptcha_script;?>

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