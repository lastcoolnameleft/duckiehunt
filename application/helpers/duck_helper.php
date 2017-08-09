<?php

    function distance($lat1, $lon1, $lat2, $lon2) {
//        print "&getDistanceTo($lat1, $lon1, $lat2, $lon2)";

		$theta = $lon1 - $lon2;
		$dist = sin(deg2rad($lat1)) * sin(deg2rad($lat2)) + cos(deg2rad($lat1)) * cos(deg2rad($lat2)) * cos(deg2rad($theta));
		$dist = acos($dist);
		$dist = rad2deg($dist);
		$miles = $dist * 60 * 1.1515;
        $distance = round($miles, 2);

        $distance = is_nan($distance) ? 0 : $distance;
		return $distance;
	}

	function send_duck_location_change_mail($to, $duck_id, $duck_location_id)
	{
		$result = false;
		$CI = get_instance(); 

        $CI->load->library('email');

		$config = array('mailtype' => 'html');
		$CI->email->initialize($config);

		$CI->email->from('tommy@duckiehunt.com', 'DuckieHunt');

		$CI->email->to($to);
//		$CI->email->bcc('tommy@duckiehunt.com', 'tommy@duckiehunt.com');

		$subject = "Duck # $duck_id has moved!";
		$CI->email->subject( $subject );

		$message = "You are receiving this email because you're on the alert list for Duck #{$duck_id}.<br/>\n";
		$message .= "You can see where this duck has travelled to by going to <a href='http://duckiehunt.com/view/duck/{$duck_id}'>http://duckiehunt.com/view/duck/{$duck_id}</a>";
		$message .= " and can see the specific location info at <a href='http://duckiehunt.com/view/location/{$duck_location_id}'>http://duckiehunt.com/view/location/{$duck_location_id}</a>";

		$CI->email->message($message);

		if ($send_result = $CI->email->send() )
		{
			$result = true;
		}
		else {
			error_log("some error happened.  send_result = {$send_result}");
			error_log(print_r($CI->email->print_debugger(), true));
		}

		return $result;

	}

    function mail_location_update_emails( $duck_id, $duck_location_id )
    {
		//  Notify Tommy
		send_duck_location_change_mail('tommy@duckiehunt.com', $duck_id, $duck_location_id);

		//  Now we notify everyone who's on the track list
        $this->db->select('email')->from('duck_track')->join('cl_users', 'duck_track.user_id=cl_users.id')->where('duck_id', $duck_id);
        $query = $this->db->get();
        $result = $query->result_array();
		foreach ($result as $user_data) {
			send_duck_location_change_mail($user_data['email'], $duck_id, $duck_location_id);
		}
        
    }
?>
