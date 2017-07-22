<?php 
    $this->load->helper('form'); 
    echo form_open('manage/create');
?>
<table border='1'>
	<tr>
		<td><?php echo anchor('manage/duck/create', 'Create Duck') ?></td>
		<td><?php echo anchor('manage/duck/edit', 'Edit Duck') ?></td>
	</tr>
</table>

<?php echo form_submit('mysubmit', 'Submit!'); ?>
<?php echo form_close(); ?>
