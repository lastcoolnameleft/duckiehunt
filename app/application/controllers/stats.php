<?php

class Stats extends CI_Controller {

	function index()
	{
		$this->load->view('header');

        $query = $this->db->query(
            'SELECT `duck_id`, COALESCE(name, "Unnamed") AS `name`, `total_distance`'
                . ' FROM `duck` WHERE `approved` = "Y" ORDER BY `total_distance` DESC LIMIT 10');
        $ducks = $query->result_array();

        $query = $this->db->query(
            "SELECT ROUND(SUM(`distance_to`)) as total_distance, `user_id`, `username`"
                . " FROM `duck_location` JOIN `users` ON (`user_id`=`id`)"
                . " WHERE `user_id` != 0 AND `approved` = 'Y'"
                . " GROUP BY (`user_id`) ORDER BY `total_distance` desc LIMIT 10");
        $users = $query->result_array();

        $params = array(
			'ducks' => $ducks,
            'users' => $users,
		);

        $this->load->view('top_distance_table_yui', $params);
		$this->load->view('footer');
	}

}
?>
