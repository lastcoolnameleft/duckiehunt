
<?php	if (!empty($duck_id) && !empty($duck_info)) { ?>
      <!-- Intro Content -->
      <h2>Location Info</h2>
      <div class="row">
        <div class="col-lg-12">

            <dl class="row">
                <dt class="col-sm-3">Name</dt>
                <dd class="col-sm-9" id="duck_name"><?php echo empty($duck_info['name']) ? 'Unnamed' : $duck_info['name'] ?></dd>
                <?php if (!empty($location_info['location'])) { ?>
                    <dt class="col-sm-3">Location</dt>
                    <dd class="col-sm-9"><?php echo $location_info['location'] ?></dd>
                <?php } ?>
                <?php if (!empty($location_info['comments'])) { ?>
                    <dt class="col-sm-3">Comments</dt>
                    <dd class="col-sm-9"><?php echo $location_info['comments'] ?></dd>
                <?php } ?>
                <?php if (!empty($location_info['date_time'])) { ?>
                    <dt class="col-sm-3">Date/Time</dt>
                    <dd class="col-sm-9"><?php echo $location_info['date_time'] ?></dd>
                <?php } ?>
                <?php if (!empty($duck_info['total_distance'])) { ?>
                    <dt class="col-sm-3">Total Distance Travelled</dt>
                    <dd class="col-sm-9"><?php echo $duck_info['total_distance'] . ' miles' ?></dd>
                <?php } ?>
                <?php if (!empty($location_info['distance_to'])) { ?>
                    <dt class="col-sm-3">Distance to this point</dt>
                    <dd class="col-sm-9"><?php echo $location_info['distance_to'] . ' miles' ?></dd>
                <?php } ?>
                <?php if (!empty($location_info['latitude'])) { ?>
                    <dt class="col-sm-3">Latitude</dt>
                    <dd class="col-sm-9"><?php echo round($location_info['latitude'], 5) ?></dd>
                <?php } ?>
                <?php if (!empty($location_info['longitude'])) { ?>
                    <dt class="col-sm-3">Longitude</dt>
                    <dd class="col-sm-9"><?php echo round($location_info['longitude'], 5) ?></dd>
                <?php } ?>
                <?php if (!empty($links)) { ?>
                    <dt class="col-sm-3">Links</dt>
                    <dd class="col-sm-9">
                        <?php foreach ($links as $link) { echo anchor($link) . "<br />"; } ?>
                    </dd>
                <?php } ?>
            </dl>
        </div>
      </div>
      <!-- /.row -->

      <!-- Photos -->
      <?php if ($photos) { ?>
        <h2>Photos</h2>
        <div class="row">
            <?php foreach ($photos as $photo_id => $thumbnail_url) { ?>
            <div class="col-lg-2 col-sm-2 mb-2">
            <img class="img-fluid" src="<?php echo str_replace('_t', '_m_d', $thumbnail_url) ?>" alt="">
            </div>
            <?php } ?>
        </div>
      <?php } ?>
      <!-- /.row -->

      <!-- Map -->
      <h2>Map</h2>
      <div class="row">
        <div class="col-lg-6">
			<div id='map'></div>
		</div>
      </div>
      <!-- /.row -->

<?php }

    if ( $can_modify ) {
        echo "<h2>Modify Duck Location</h2>";
        echo "<input type='button' name='edit_loc' onClick='document.location=\"/mark/update/{$duck_location_id}\"' value='Edit Location' />";
    }
        ?>
</div>
<br />