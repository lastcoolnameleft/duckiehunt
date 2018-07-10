<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Sendgrid {
    public function __construct()
    {
		$CI =& get_instance();
		$CI->load->library('email');
		$CI->config->load('duckiehunt');

		$CI->email->initialize(array(
			'protocol' => 'smtp',
			'smtp_host' => 'smtp.sendgrid.net',
			'smtp_user' => $CI->config->item('sendgrid_username'),
			'smtp_pass' => $CI->config->item('sendgrid_password'),
			'smtp_port' => 587,
			'crlf' => "\r\n",
			'newline' => "\r\n",
			'mailtype' => 'html',
		));
	}

	public function send($to, $subject, $message) {
		$CI =& get_instance();
		$CI->email->from('tommy@duckiehunt.com', 'DuckieHunt');
		$CI->email->to($to);
		$CI->email->subject($subject);
		$CI->email->message($message);
		$result = $CI->email->send();
		if ( ! $result ) {
			error_log('Got error using sendmail');
			error_log(print_r($CI->email->print_debugger(), true));
		}
		return $result;
	}

	public function send_duck_location_change($to, $duck_id, $duck_location_id)
	{
		$subject = "Duck # $duck_id has moved!";

		$message = "You are receiving this email because you're on the alert list for Duck #{$duck_id}.<br/>\n";
		$message .= "You can see where this duck has travelled to by going to <a href='http://duckiehunt.com/view/duck/{$duck_id}'>http://duckiehunt.com/view/duck/{$duck_id}</a>";
		$message .= " and can see the specific location info at <a href='http://duckiehunt.com/view/location/{$duck_location_id}'>http://duckiehunt.com/view/location/{$duck_location_id}</a>";

		$result = $this->send($to, $subject, $message);

		return $result;
	}


}
