<div class="container">

      <!-- Page Heading/Breadcrumbs -->
      <h1 class="mt-4 mb-3">Login
      </h1>

      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <a href="/">Home</a>
        </li>
        <li class="breadcrumb-item active">Login</li>
      </ol>


  <link rel="stylesheet" href="/css/login_style.css" />
  <link rel="stylesheet" href="/css/login-style.css" />

  <div id="infoMessage"><?php echo $message;?></div>

      <!-- Intro Content -->
      <div class="row">
        <div class="col-lg-8">
          <p>To provide better security, we use the following options to log into Duckiehunt:</p>
          <div id="auth_wrapper">
            <div id="auth_container">
              <div id="login_container">
                <div id="social_login">
                  <a class="fb_login" href="<?php echo $fb_auth_url ?>"><span></span>Facebook</a>
                  <a class="gg_login" href="<?php echo $g_auth_url ?>"><span></span>Google</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- /.row -->

</div>