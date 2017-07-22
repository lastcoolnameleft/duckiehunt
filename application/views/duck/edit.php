<?php 
    $this->load->helper('form'); 
    echo form_open('manage/duck/update', array('id' => 'form', 'name' => 'form'));
    echo form_hidden('duck_id', $edit_duck_info['duck_id']);
    echo form_hidden('action', 'edit');
?>
Edit a Duckie:</br>
<?php echo form_dropdown('duck_to_edit', $duck_list, $edit_duck_info['duck_id'], 'onChange="javascript:formHandler()"' ); ?>
</br>
</br>

<SCRIPT LANGUAGE="JavaScript">
function formHandler(form){
var URL = '<?php echo $base_url; ?>index.php/manage/duck/edit/' + document.form.duck_to_edit.options[document.form.duck_to_edit.selectedIndex].value;
window.location.href = URL;
}
</script>
<table>
	<tr><td>ID:</td><td><?php echo $edit_duck_info['duck_id'] ?></td></tr>
	<tr><td>Name:</td><td><?php echo form_input('name', $edit_duck_info['name']); ?></td></tr>
	<tr><td>Comments:</td><td><?php echo form_textarea( array('name' => 'comments', 'id' => 'comments', 'rows' => 4, 'cols' => 30, 'value' => $edit_duck_info['comments'])) ?></td></tr>
</table>

<?php echo form_submit('mysubmit', 'Submit!'); ?>
<?php echo form_close(); ?>
