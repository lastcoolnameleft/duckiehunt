<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en-AU">
<head>
  <title>duckiehunt.com</title>
  <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
  <meta name="author" content="fullahead.org" />
  <meta name="keywords" content="Open Web Design, OWD, Free Web Template, Lazy Days, Fullahead" />
  <meta name="description" content="Webtracking for the coolest ducks on the planet." />
  <meta name="robots" content="index, follow, noarchive" />
  <meta name="googlebot" content="noarchive" />
  <link rel="icon" type="image/png" href="/images/icons/duck-32x32.png" />
  <link  href="/css/html.css" media="screen, projection, tv " rel="stylesheet" type="text/css" />
  <link  href="/css/layout.css" media="screen, projection, tv " rel="stylesheet" type="text/css" />
  <link  href="/css/print.css" media="print " rel="stylesheet" type="text/css" />
</head>
<body>

<div id="content">

  <div id="header">

    <div id="title">
      <h1>duckie hunt</h1>
    </div>
    <img src="/images/bg/balloons.gif"  alt="baloons"  class="balloons" />
    <img src="/images/bg/header_left.jpg"  alt="baloons"  class="left" />
    <img src="/images/bg/header_right.jpg"  alt="baloons"  class="right" />

  </div>

  <div id="mainMenu">
    <ul class="floatRight">
<?php
    $this->load->helper('html');
	$controller = $this->uri->rsegment(1);

	echo "\t\t<li>" . anchor('main', 'Main', $controller == 'main' ? array('class' => 'here') : '') . "</li>\n";
	echo "\t\t<li>" . anchor('stats', 'Stats', $controller == 'stats' ? array('class' => 'here') : '') . "</li>\n";
	echo "\t\t<li>" . anchor('view', 'View', $controller == 'view' ? array('class' => 'here') : '') . "</li>\n";
    echo "\t\t<li>" . anchor('mark', 'Mark', $controller == 'mark' ? array('class' => 'here') : '') . "</li>\n";

    if ($controller == 'user') {
        echo "\t\t<li>" . anchor('user', 'user', $controller == 'user' ? array('class' => 'here') : '') . "</li>\n";
    }
/*
	if ($this->dx_auth->get_role_id() == 2) {
    	echo "\t\t<li>" . anchor('history', 'History', $controller == 'history' ? array('class' => 'here') : '') . "</li>\n";
		echo "\t\t<li>" . anchor('admin', 'Admin', ($controller == 'admin' || $controller == 'duck') ? array('class' => 'here') : '') . "</li>\n";
	}
*/
	echo "\t\t<li>" . anchor('faq', 'Faq', $controller == 'faq' ? array('class' => 'here') : '') . "</li>\n";
  /*
	if ( $this->dx_auth->is_logged_in() ) {
		  echo '<li>' . anchor('auth/logout', 'logout', $controller == 'auth' ? array('class' => 'here') : '') . '</li>';
	} else {
		  echo '<li>' . anchor('auth/login', 'login', $controller == 'auth' ? array('class' => 'here') : '') . '</li>';
	}
  */
?>
    </ul>
  </div>

  <div id="page">


