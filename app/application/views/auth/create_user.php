<h1><?php echo lang('create_user_heading');?></h1>
<p><?php echo lang('create_user_subheading');?></p>

<div id="infoMessage"><?php if ($message) { echo "<b><font color='red'>$message</font></b>"; } ?></div>

<?php echo form_open("auth/create_user");?>

      <?php
      if($identity_column!=='email') {
          echo '<p>';
          echo lang('create_user_identity_label', 'identity');
          echo form_error('identity');
          echo form_input($identity);
          echo '</p>';
      }
      ?>

     <p>
            <?php echo lang('create_user_email_label', 'email');?>
            <?php echo form_input($email);?>
      </p>

      <p>
            <?php echo lang('create_user_password_label', 'password');?>
            <?php echo form_input($password);?>
      </p>

      <p>
            <?php echo lang('create_user_password_confirm_label', 'password_confirm');?>
            <?php echo form_input($password_confirm);?>
      </p>

      <p>
            <?php echo lang('create_user_validation_agree_user_guidelines_label', 'agree_user_guidelines');?>
            <input type="checkbox" name="agree_user_guidelines" value="1" id="agree_user_guidelines">
      </p>


      <p><?php echo form_submit('submit', lang('create_user_submit_btn'), array('id' => 'submit'));?></p>

<?php echo form_close();?>
