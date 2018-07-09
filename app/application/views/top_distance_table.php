<br/>
<h2>Top Movers and Quakers</h2>

<table>
	<tr>
		<th>Duck</th>
		<th>Distance</th>
	</tr>

<?php foreach ($ducks as $duck) { ?>
	<tr>
		<td>
			<?php echo anchor('view/duck/' . $duck['duck_id'], $duck['duck_id']) .
				(empty($duck['name']) ? '' : " ({$duck['name']})" )?></td>
		<td><?php echo $duck['total_distance'] ?></td>
	</tr>
<?php } ?>
</table>
