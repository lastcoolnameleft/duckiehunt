<?php 
    $this->load->helper('form'); 
    echo form_open('manage/duck/assign_s', array('id' => 'form', 'name' => 'form'));

$form = $this->form_validation;

$username = array(
'name'  => 'username',
'id'    => 'username',
'maxlength' => $this->config->item('CL_username_max'),
'size'  => 30,
'value' => isset($form->username) ? $form->username : '');


$password = array(
'name'  => 'password',
'id'    => 'password',
'maxlength' => $this->config->item('CL_password_max'),
'size'  => 30,
'value' => isset($form->password) ? $form->password : '');

$password_conf = array(
'name'  => 'password_confirm',
'id'    => 'password_confirm',
'maxlength' => $this->config->item('CL_password_max'),
'size'  => 30,
'value' => isset($form->password_confirm) ? $form->password_confirm : '');

$email = array(
'name'  => 'email',
'id'    => 'email',
'maxlength' => 80,
'size'  => 30,
'value' => isset($form->email) ? $form->email : '');

	
?>
Assign a Duckie:</br>
<table>
	<tr>
		<td>Duckie</td>
		<td><?php echo form_dropdown('duck_id', $duck_list ); ?></td>
	</tr>
	<tr>
		<td>Person</td>
		<td><?php echo form_dropdown('user_id', $user_list); ?></td>
	</tr>
	<tr>
		<td>Or new account</td>
		<td>
			<table>
				<tr>
					<td>Username</td>
					<td><?php echo form_input($username)?>    <?php //echo $form->username_error;?></td>
				</tr>
					<td>pass</td>
					<td><?php echo form_input($password)?>    <?php //echo $form->username_error;?></td>
				</tr>
				<tr>
					<td>email</td>
					<td><?php echo form_input($email)?>    <?php //echo $form->username_error;?></td>
				</tr>
			</table>
		</td>
	</tr>
</table>

<?php echo form_submit('mysubmit', 'Submit!'); ?>
<?php echo form_close(); ?>
