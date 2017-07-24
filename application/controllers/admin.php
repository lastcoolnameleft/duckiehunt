<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Admin extends CI_Controller {

	public function __construct()
	{
        parent::__construct();
        $this->dx_auth->check_uri_permissions();
	}

	function index()
	{
		$data['page_title'] = 'Your title';
		$this->load->view('header');
		$this->load->view('admin');
		$this->load->view('footer');
	}

	function create()
	{
		$data = array(
		'duck_id' => $this->input->post('duckie_id'),
		'name' => $this->input->post('duckie_name', 'Blank'),
		'comments' => $this->input->post('comments'),
		);
		$this->db->insert('duck', $data); 
		redirect('/manage', 'refresh');
	}
}
?>
