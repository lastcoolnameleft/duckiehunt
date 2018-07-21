<?php

class Login extends Controller {

   function index()
   {
      $data['page_title'] = 'Your title';
      $this->load->view('header');
      $this->load->view('login');
      $this->load->view('footer');
   }

}
?>
