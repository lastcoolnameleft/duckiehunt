<?php

class Admin extends Controller {

	function __construct()
	{
        parent::Controller();
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
