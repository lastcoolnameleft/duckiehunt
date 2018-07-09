<table>
		<tr>
            <?php echo (!empty($user_duck_list)) ? '<td>Tracked Ducks:</td>' : ''; ?>
			<td>All Ducks:</td>
            <?php echo (!empty($duck_location_pulldown)) ? '<td>Duck Locations:</td>' : '' ; ?> 

        </tr>
		<tr>

            <?php echo (!empty($user_duck_list)) ? '<td>' . form_dropdown('user_duck_id', $user_duck_list, $duck_id, 'onChange="javascript:redirectToDuck(this)"' ) . '</td>' : ''; ?>

            <td><?php echo form_dropdown('total_duck_id', $total_duck_list, $duck_id, 'onChange="javascript:redirectToDuck(this)"' ); ?></td>
            <td><?php echo (!empty($duck_location_pulldown)) ? form_dropdown('duck_location_id', $duck_location_pulldown, $duck_location_id, 'onChange="javascript:redirectToDuckLocation(this)"' ) : ''; ?></td>

        </tr>
</table>

<script type="text/javascript" language="JavaScript">
function redirectToDuck(obj)
{
	var duck_id = obj[obj.selectedIndex].value;
	var URL = '<?php echo $base_url; ?>view/duck/' + duck_id;
	window.location.href = URL;
}

function redirectToDuckLocation(obj)
{
	var location_id = obj[obj.selectedIndex].value;
	var URL = '<?php echo $base_url; ?>view/location/' + location_id;
	window.location.href = URL;
}
</script>