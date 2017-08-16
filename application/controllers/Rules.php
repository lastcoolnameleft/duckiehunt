<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Rules extends CI_Controller {

	public function index()
	{
		$this->load->view('header');
		$this->load->view('user_guidelines');
		$this->load->view('footer');
	}
}
