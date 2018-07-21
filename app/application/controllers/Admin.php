<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Admin extends CI_Controller {

	public function __construct()
	{
        parent::__construct();
		if (!$this->ion_auth->is_admin()) {
			return show_error('You must be an administrator to view this page.');
		}
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
