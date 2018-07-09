<?php

class Invite extends CI_Controller {

	function index()
	{
		$this->load->view('header');
		$this->load->view('invite/main');
		$this->load->view('footer');
	}

	function submit()
	{
		$this->load->library('sendgrid');
		$email = $this->input->post('email');

		$subject = 'You have been invited to join duckiehunt.com!';
		$message = "This is not a spam message.<br/>No really.<br/>Someone thought you were cool enough to register at <a href='http://duckiehunt.com'>duckiehunt.com</a>.<br/>
		Register <a href='http://duckiehunt.com/auth/create_user'>here</a>.<br/>
		Check out cool stuff <a href='http://duckiehunt.com/view'>here</a><br/>
		<br/>
		Thanks!<br/>
		Duckiehunt.com";

		$this->sendgrid->send($email, $subject, $message);

		$redirect_url = $result ? '/invite/fail' : '/invite/success';
		redirect($redirect_url, 'refresh');
	}

	function success()
	{
        $this->load->view('header');
        $this->load->view('invite/success');
        $this->load->view('invite/main');
        $this->load->view('footer');
	}

	function fail()
	{
        $this->load->view('header');
        $this->load->view('invite/fail');
        $this->load->view('invite/main');
        $this->load->view('footer');
	}
	
}

?>
