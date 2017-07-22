<?php

class Alert extends Controller
{
	function duck( $duck_id )
	{
//        $this->cl_auth->check();
		$user_id = $this->dx_auth->get_user_id();
		$this->load->model('duck_model', 'duck');
		$this->duck->track( $duck_id, $user_id );

		
        $this->load->view('header');
        $this->load->view('alert/success');
        $this->load->view('footer');

        redirect('view/duck/' . $this->input->post('duck_id'), 'refresh');

	}

}
