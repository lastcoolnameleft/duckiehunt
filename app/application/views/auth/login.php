<link rel="stylesheet" href="/css/login_style.css" />
<link rel="stylesheet" href="/css/login-style.css" />

<div id="infoMessage"><?php echo $message;?></div>

<div id="auth_wrapper">
  <div id="auth_container">
    <div id="login_container">
      <h2 class="signup_heading">Login to your account.</h2>
      <div id="social_login">
        <a class="fb_login" href="<?php echo $fb_auth_url ?>"><span></span>Facebook Login</a>
        <a class="gg_login" href="<?php echo $g_auth_url ?>"><span></span>Google Login</a>
      </div>
      <div class="login_or"></div>
        <div id="div_error_box_login" ></div>
        <?php echo form_open("auth/login");?>
        <ul>
          <li>
            <input type="text" name="identity" id="identity" value="" placeholder="Username" class="required requiredField Email fg-input text fg-fw" autocomplete="off" style="">
          </li>
          <li>
            <input type="text" name="password" id="password" value="" placeholder="Password" class="required requiredField Password fg-input text fg-fw" autocomplete="off" style="">
          </li>
          <li>
            <div class="chkbox"><?php echo form_checkbox('remember', '1', FALSE, 'id="remember"');?> Remember me
          </li>
          <li>
            <?php echo form_submit('submit', lang('login_submit_btn'), array('id' => 'submit'));?>
          </li>
        </ul>
    <?php echo form_close();?>
    <div>
        <a class="forgot-password" href="forgot_password">Forgot Password?</a>
        <a href='create_user' id="register" class="signup-btn">Create New Account</a>
        <div class="clearfix"></div>
    </div>
  </div>
</div>