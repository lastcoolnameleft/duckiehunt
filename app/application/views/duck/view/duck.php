      <!-- Intro Content -->
      <div class="row">
        <div class="col-lg-6">
          <h2><?php echo $duck_info['name'] ?></h2>
          <p>Distance Travelled:  <?php echo $duck_info['total_distance'] ?> Miles</p>
		  <?php echo (!empty($duck_info['comments']) ? $duck_info['comments'] : '')  ; ?>
        </div>
      </div>
      <!-- /.row -->

      <!-- Photos -->
      <h2>Photos</h2>
      <div class="row">
		<?php foreach ($photos as $photo_id => $thumbnail_url) { ?>
        <div class="col-lg-2 col-sm-2 mb-2">
          <img class="img-fluid" src="<?php echo str_replace('_t', '_m_d', $thumbnail_url) ?>" alt="">
		</div>
		<?php } ?>
      </div>
      <!-- /.row -->

      <!-- Team Members -->
      <h2>Locations</h2>

      <div class="row">
		<?php foreach ($duck_location_list as $duck_location) { ?>
        <div class="col-lg-4 mb-4">
          <div class="card h-100 text-center">
            <!-- <img class="card-img-top" src="http://placehold.it/750x450" alt=""> -->
            <div class="card-body">
              <h4 class="card-title"><?php echo anchor( '/view/location/' . $duck_location['duck_location_id'], $duck_location['location']) ?></h4>
              <h6 class="card-subtitle mb-2 text-muted"><?php echo $duck_location['date_time'] ?></h6>
              <h6 class="card-text"><?php echo $duck_location['comments'] ?></h6>
            </div>
          </div>
        </div>
		<?php } ?>
      </div>
      <!-- /.row -->
		</div>

