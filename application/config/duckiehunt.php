<?php
defined('BASEPATH') OR exit('No direct script access allowed');

$config['auto_approve'] = getenv('DH_AUTO_APPROVE');
$config['facebook_client_id'] = getenv('FACEBOOK_CLIENT_ID');
$config['facebook_client_secret'] = getenv('FACEBOOK_CLIENT_SECRET');
$config['google_client_id'] = getenv('GOOGLE_CLIENT_ID');
$config['google_client_secret'] = getenv('GOOGLE_CLIENT_SECRET');