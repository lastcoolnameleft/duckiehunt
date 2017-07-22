
<table>
		<tr>
			<?php echo (!empty($user_duck_list))  ? '<td>Tracked Ducks:</td>' : '' ?>
			<td>All Ducks:</td></tr>
		<tr>
			<?php echo (!empty($user_duck_list))  ? '<td>' . form_dropdown('user_duck_id', $user_duck_list, $duck_id, 'onChange="javascript:formHandler(this)"' ) . '</td>' : ''; ?>
			<td><?php echo form_dropdown('total_duck_id', $total_duck_list, $duck_id, 'onChange="javascript:formHandler(this)"' ); ?></td></tr>
</table>

<script type="text/javascript" language="JavaScript">
function formHandler(obj)
{
	var duck_id = obj[obj.selectedIndex].value;
	var URL = '<?php echo $base_url; ?>index.php/history/duck/' + duck_id;
	window.location.href = URL;
}
</script>

<?php if ( !empty($duck_history) )  { ?>
Duckie History:</br>

<table border=1>
	<tr>
		<td>Duck #</td>
		<td>Name</td>
		<td>Action</td>
		<td>Time</td>
		<td>Details</td>
		<?php if ($can_modify) { echo "<td>Action</td>"; } ?>
	</tr>
<?php  foreach ($duck_history as $duck) { ?>
    <tr>
        <td><nobr><?php echo $duck['duck_id'] ?></nobr></td>
        <td><nobr><?php echo empty($duck['duck_name']) ? 'Unnamed' : $duck['duck_name'] ?></nobr></td>
<!--        <td><?php echo $duck['username'] ?></td> -->
        <td><?php echo $duck['action'] ?></td>
        <td><nobr><?php echo $duck['timestamp'] ?> CST</nobr></td>
<!--        <td><nobr><?php echo date('d/m/Y H:i', $duck['timestamp']) ?></nobr></td> -->
        <td><?php 
switch ($duck['action_id']) {
	case 1:
		$result = 'Created';
		break;
	case 2:
		$result = 'Info Updated';
		break;
	case 3:
		$result = "Now assigned to {$duck['assign_username']}";	
		break;
	case 4:
		$username = empty($duck['mark_username']) ? 'Anonymous' : $duck['mark_username'];
		$result = "{$username} added a new " . anchor("view/duck/{$duck['duck_id']}", "marker");
		$result = empty($duck['location']) ? $result : $result . " in " . $duck['location'];
		
		break;
	case 5:
		$result = "{$duck['track_username']} is now tracking this duck";	
		break;
	default:
		$result = '';

}
echo $result;
?></td>
		<?php 
	if ($can_modify && !empty($duck['duck_location_id'])) { 
		echo "<td><a href='/manage/location/delete/{$duck['duck_location_id']}'>Delete</a></td>"; 
	} 
		?>
    </tr>
<?php	} ?>
<?php } ?>

</table>
