<?php

class Invite extends Controller {

	function index()
	{
        $this->load->view('header');
        $this->load->view('invite/main');
        $this->load->view('footer');
	}

	function submit()
	{
		$email = $this->input->post('email');

		$result = true;

		if (valid_email($email)) {

			$data = array(
				'to' => $email,
				'subject' => 'You have been invited to join duckiehunt.com!',
				'message' => "This is not a spam message.<br/>No really.<br/>Someone thought you were cool enough to register at <a href='http://duckiehunt.com'>duckiehunt.com</a>.<br/>
Register <a href='http://duckiehunt.com/auth/register'>here</a>.<br/>
Check out cool stuff <a href='http://duckiehunt.com/view'>here</a><br/>
<br/>
Thanks!<br/>
Duckiehunt.com"
			);

			$this->load->model('duck_model', 'duck');
			$result = $this->duck->send_mail($data);
		}

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
