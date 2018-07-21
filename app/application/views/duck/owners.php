<?php 
    $this->load->helper('form'); 
    echo form_open('manage/duck/assign_s', array('id' => 'form', 'name' => 'form'));
?>
Duckie Assignments:</br>
<table border=1>
<?php 
foreach ($duck_list as $duck) {
	echo "\t\t<tr><td>{$duck['duck_name']}</td><td>{$duck['username']}</td></tr>\n";
}
?>
</table>

<?php echo form_close(); ?>
