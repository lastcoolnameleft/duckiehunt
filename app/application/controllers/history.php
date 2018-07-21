<?php

class History extends CI_Controller {

	function index()
	{
		if (!$this->ion_auth->is_admin()) {
			return show_error('You must be an administrator to view this page.');
		}
		$this->duck();
	}

	function duck( $duck_id = 0 )
	{
		//  Total Duck List
        $this->db->select('duck_id, name')->from('duck')->order_by('duck_id');
        $query = $this->db->get();

        $total_duck_list = count($query->result_array()) ? array('' => '') : array();
        foreach ($query->result_array() as $row) {
            $name = (empty($row['name']) ? 'Unnamed '  : $row['name']) . " ({$row['duck_id']})";
            $total_duck_list[$row['duck_id']] = $name;
        }

        $data['total_duck_list'] = $total_duck_list;

		//  User's Duck List 
        $this->db->select('duck.duck_id, name')->from('duck_track')->join('duck', 'duck.duck_id=duck_track.duck_id')->where('user_id', $this->ion_auth->get_user_id());
        $query = $this->db->get();

        $user_duck_list = count($query->result_array()) ? array('' => '') : array();
        foreach ($query->result_array() as $row) {
            $name = (empty($row['name']) ? 'Unnamed '  : $row['name']) . " ({$row['duck_id']})";
            $user_duck_list[$row['duck_id']] = $name;
        }

        $data['user_duck_list'] = $user_duck_list;

		//  Duck History
		if ( !empty($duck_id) ) {
			$this->db->
				select('duck.duck_id, duck.name as duck_name, user_assign.username as assign_username, user_track.username as track_username, user_mark.username as mark_username, duck_location.latitude, duck_location.longitude, duck_history_action.action as action, duck_history.timestamp, action_id, duck_location.location as location, duck_location.duck_location_id as duck_location_id')
					->from('duck_history')
					->join('duck', 'duck.duck_id=duck_history.duck_id')
					->join('duck_history_action', 'duck_history.action_id=duck_history_action.duck_history_action_id')
					->join('duck_assign', 'duck_history.duck_history_id=duck_assign.duck_history_id', 'left')
					->join('users as user_assign', 'user_assign.id=duck_assign.user_id', 'left')
					->join('duck_track', 'duck_history.duck_history_id=duck_track.duck_history_id', 'left')
					->join('users as user_track', 'user_track.id=duck_track.user_id', 'left')
					->join('duck_location', 'duck_history.duck_history_id=duck_location.duck_history_id', 'left')
					->join('users as user_mark', 'user_mark.id=duck_location.user_id', 'left')
					->where('duck_history.duck_id', $duck_id)
					->order_by('duck_history.timestamp', 'desc');
			$query = $this->db->get();
			$data['duck_history'] = $query->result_array();
		}

		$data['base_url'] = $this->config->item('base_url');
		$data['duck_id'] = $duck_id;
		$data['page_title'] = 'Your title';
		$data['can_modify'] = $this->ion_auth->in_group($this->config->item('admin_group', 'ion_auth'));

		$this->load->view('header');
		$this->load->view('duck/history', $data);
		$this->load->view('footer');
	}

}
?>
