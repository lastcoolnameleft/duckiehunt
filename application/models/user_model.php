<?php

class User_model Extends Model {

    function User_model()
    {
        parent::Model();
    }

	function getUserIdFromEmail( $email ) 
	{
        $this->db->select('user_id')->from('duck_user')->where('email', $email);
        $query = $this->db->get();

        $result = $query->result_array();
        $distance = 0;
        if ( empty($result) ) {
			return NULL;	
		}
		else {
			return $result;
		}
	}	

	function getOrCreateUser( $email, $first_name, $last_name )
	{
		if ( $user_id == $this->getUserIdFromEmail($email) ) {
			return $user_id;
		}
		else {
			return $this->createUser( $email );
		}
	}

	function createUser( $email, $first_name = null, $last_name = null)
	{
        $data = array(
            'email' => $email,
        );
        $this->db->insert('duck_user', $data);
        return $this->db->insert_id();
	}		
}
?>
