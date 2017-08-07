<?php
/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


class User extends CI_Controller {

    function index()
    {
        $this->load->view('header');
        $this->load->view('footer');
    }

    function view($username)
    {
        $this->db->select('id, username')->from('users')->where('username', $username);
        $query = $this->db->get();

        if ($query->num_rows()) {
            $user_info = $query->row_array();

            $this->db->select('duck_location_id, duck_id, location, latitude, longitude, distance_to')
                    ->from('duck_location')
						->where('approved', 'Y')
                        ->where('user_id', $user_info['id'])
                        ->where('distance_to !=', 0 );
            $query = $this->db->get();
            $location_list = $query->result_array();

            $total_distance = 0;
            foreach ($location_list as $location) {
                $total_distance += $location['distance_to'];
            }
            $data = array(
                'user_info' => $user_info,
                'location_list' => $location_list,
                'total_distance' => $total_distance,
                );


            $this->load->view('header');
            $this->load->view('user/user_info', $data);
            $this->load->view('user/user_map', $data);
            $this->load->view('footer');
         }
        else {
            show_404();
        }

    }
}