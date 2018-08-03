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

		$message = "Welcome fellow <a href='https://www.duckiehunt.com'>Duckiehunt</a> friend.<br/>\n<br/>\n";
		$message .= "You can see where this duck has travelled to by going to: <a href='https://www.duckiehunt.com/view/location/{$duck_location_id}'>https://www.duckiehunt.com/view/location/{$duck_location_id}</a>.<br/>\n<br/>\n";
		$message .= "You are receiving this email because you're on the alert list for Duck #{$duck_id}.";
		$message .= "To remove yourself from notification for this duck, please go to: <a href='https://www.duckiehunt.com/view/duck/{$duck_id}'>https://www.duckiehunt.com/view/duck/{$duck_id}</a> and click 'Release me!'<br/>\n";

		$result = $this->send($to, $subject, $message);

		return $result;
	}


}
