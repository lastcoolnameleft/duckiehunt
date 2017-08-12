<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Sendgrid {
    public function __construct()
    {
		$CI =& get_instance();
		$CI->load->library('email');

		$CI->email->initialize(array(
			'protocol' => 'smtp',
			'smtp_host' => 'smtp.sendgrid.net',
			'smtp_user' => getenv('SENDGRID_USERNAME'),
			'smtp_pass' => getenv('SENDGRID_PASSWORD'),
			'smtp_port' => 587,
			'crlf' => "\r\n",
			'newline' => "\r\n"
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
}
