<?php

class Location extends CI_Controller {

    function __construct()
    {
        parent::__construct();
		if (!$this->ion_auth->is_admin()) {
			return show_error('You must be an administrator to view this page.');
		}
    }

	function delete( $duck_location_id ) {
        $this->load->model('duck_model', 'duck');
        $duck_id = $this->duck->deleteLocation( $duck_location_id );

//		$this->db->delete('duck_location', array('duck_location_id' => $duck_location_id));
		redirect('/history/duck/' . $duck_id, 'refresh');	
	}

	
}
?>
