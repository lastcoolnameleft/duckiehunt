<?php

class Duck extends CI_Controller {

    function __construct()
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
      $this->load->view('footer');
   }

	function create()
	{
		$data['page_title'] = 'Your title';
		$this->load->view('header');
		$this->load->view('duck/create');
		$this->load->view('footer');
	}

	function edit( $duck_id = 0 )
	{
		$this->db->select('duck_id, name')->from('duck')->order_by('duck_id');
		$query = $this->db->get();

		$duck_list = array( '' => '' );
		foreach ($query->result_array() as $row) {
            $name = (empty($row['name']) ? 'Unnamed '  : $row['name']) . " ({$row['duck_id']})";
			$duck_list[$row['duck_id']] = $name;
		}
		$data['base_url'] = $this->config->item('base_url');
		$data['duck_list'] = $duck_list;

		$this->db->select('duck_id, name, comments')->from('duck')->where('duck_id', $duck_id);
		$query = $this->db->get();
		$data['edit_duck_info'] = $query->row_array();

		if (empty($data['edit_duck_info'])) {
			$data['edit_duck_info'] = array('duck_id' => '', 'name' => '', 'comments' => '');
		}
		$this->load->view('header');
		$this->load->view('duck/edit', $data);
		$this->load->view('footer');
	}

	function assign()
	{
		$this->load->library('form_validation');
		$data['base_url'] = $this->config->item('base_url');

		$this->db->select('id, username')->from('cl_users');
		$query = $this->db->get();
		$user_list = array( '' => '' );
		foreach ($query->result_array() as $row) {
			$user_list[$row['id']] = $row['username'];	
		}
		$data['user_list'] = $user_list;

		$this->db->select('duck_id, name')->from('duck');
		$query = $this->db->get();

		$duck_list = array( '' => '' );
		foreach ($query->result_array() as $row) {
			$duck_list[$row['duck_id']] = '#' . $row['duck_id'] . ' - ' . $row['name'];	
		}
		$data['duck_list'] = $duck_list;


		$this->load->view('header');
		$this->load->view('duck/assign', $data);
		$this->load->view('footer');
	}

	function owners()
	{
		$this->db->select('cl_users.id, cl_users.username, duck.duck_id, duck.name AS duck_name')->from('duck')->join('cl_users', 'duck.current_owner_id= cl_users.id', 'left');
		$query = $this->db->get();
		$data['duck_list'] = $query->result_array();

		$this->load->view('header');
		$this->load->view('duck/owners', $data);
		$this->load->view('footer');
	}

//  Submit functions
	function insert()
	{
		$this->load->model('duck_model', 'duck');

		$user_id = $this->ion_auth->get_user_id();
		$duck_id = $this->input->post('duck_id');
		$home_lat = '32.8466306766219';
		$home_lon = '-96.7279136180878';

		$this->duck->createUnlessExists($duck_id, $user_id, $this->input->post('name', ''), $this->input->post('comments'), 'Y' );

		redirect('/admin', 'refresh');
	}

	function update()
	{
		$user_id = $this->ion_auth->get_user_id();
		$duck_id = $this->input->post('duck_id');
		$this->load->model('duck_model', 'duck');

		$duck_history_id = $this->duck->addHistory($duck_id, $user_id, 2 );

		$data = array(
			'name' => $this->input->post('name', 'Blank'),
			'comments' => $this->input->post('comments'),
		);
		$this->db->where('duck_id', $this->input->post('duck_id'));
		$this->db->update('duck', $data); 
		redirect('/admin', 'refresh');
	}

	function assign_s()
	{
		$user_id = $this->input->post('user_id');
		$duck_id = $this->input->post('duck_id');

/*
		if (empty($user_id)) {
			$user_info = $this->cl_auth->register(
				$this->input->post('username'),
				$this->input->post('password'),
				$this->input->post('email')
			);
			$user_id = $user_info['id'];
//			error_log(print_r($user_info, true));
		}
*/
//		error_log("userid={$user_id}, duck_id={$duck_id}");
		if (!empty($user_id) && !empty($duck_id)) {
			$this->load->model('duck_model', 'duck');
			$this->duck->assign( $duck_id, $user_id );
		}
	
		redirect('/admin', 'refresh');

	}
}
?>
