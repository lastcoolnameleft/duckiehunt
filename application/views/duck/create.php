<?php 
    $this->load->helper('form'); 
    echo form_open('manage/duck/insert');
    echo form_hidden('action', 'create');
?>
Create a Duckie:</br>

<table>
	<tr><td>ID:</td><td><?php echo form_input('duck_id', ''); ?></td></tr>
	<tr><td>Name:</td><td><?php echo form_input('name', ''); ?></td></tr>
	<tr><td>Comments:</td><td><?php $data = array('name' => 'comments', 'id' => 'comments', 'rows' => 4, 'cols' => 30); echo form_textarea($data); ?></td></tr>
</table>

<?php echo form_submit('mysubmit', 'Submit!'); ?>
<?php echo form_close(); ?>
