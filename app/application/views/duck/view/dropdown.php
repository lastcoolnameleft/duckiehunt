    <!-- Page Content -->
    <div class="container">

      <!-- Page Heading/Breadcrumbs -->
      <h1 class="mt-4 mb-3">View a Duck
      </h1>

      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <a href="/">Home</a>
        </li>
		<?php 
			if ($duck_id) {
				if ($duck_location_id) {
					echo "<li class='breadcrumb-item'><a href='/view'>View</a></li>"
						. "<li class='breadcrumb-item'><a href='/view/duck/{$duck_id}'>Duck #{$duck_id}</a></li>"
						. "<li class='breadcrumb-item active'>Location #{$duck_location_id}</li>";
				} else {
					echo "<li class='breadcrumb-item'><a href='/view'>View</a></li>"
						. "<li class='breadcrumb-item'>Duck #{$duck_id}</li>";
				}
			} else {
				echo "<li class='breadcrumb-item'><a href='/view'>View</a></li>";
			}
		?>
      </ol>

      <!-- Intro Content -->
      <div class="row">
        <div class="col-lg-6">
			<table>
					<tr>
						<?php echo (!empty($user_duck_list)) ? '<td>Tracked Ducks:</td>' : ''; ?>
						<td>All Registered Ducks:</td>
						<?php echo (!empty($duck_location_pulldown)) ? '<td>Duck Locations:</td>' : '' ; ?> 

					</tr>
					<tr>

						<?php echo (!empty($user_duck_list)) ? '<td>' . form_dropdown('user_duck_id', $user_duck_list, $duck_id, 'onChange="javascript:redirectToDuck(this)"' ) . '</td>' : ''; ?>

						<td><?php echo form_dropdown('total_duck_id', $total_duck_list, $duck_id, 'onChange="javascript:redirectToDuck(this)"' ); ?></td>
						<td><?php echo (!empty($duck_location_pulldown)) ? form_dropdown('duck_location_id', $duck_location_pulldown, $duck_location_id, 'onChange="javascript:redirectToDuckLocation(this)"' ) : ''; ?></td>

					</tr>
			</table>

		</p>
		</p>
<script type="text/javascript" language="JavaScript">
	function redirectToDuck(obj)
	{
		var duck_id = obj[obj.selectedIndex].value;
		var URL = '<?php echo $base_url; ?>/view/duck/' + duck_id;
		window.location.href = URL;
	}

	function redirectToDuckLocation(obj)
	{
		var location_id = obj[obj.selectedIndex].value;
		var URL = '<?php echo $base_url; ?>/view/location/' + location_id;
		window.location.href = URL;
	}
</script>
        </div>
      </div>
	  <!-- /.row -->

	