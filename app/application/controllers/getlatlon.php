<?php

class Getlatlon extends Controller {

	function index( )
	{
        error_reporting(E_ALL);
		$request = 'http://api.local.yahoo.com/MapsService/V1/geocode';
		$request .= '?appid=' . $this->config->item('y_app_id')
					. '&location=' . rawurlencode($this->input->post('loc') )
					. '&output=php';

/*
        $response = file_get_contents($request);

        if ($response === false) {
            die('Request failed');
        }
        $responseArray = unserialize($response);
		echo json_encode($responseArray['ResultSet']['Result']);
*/
		// Initialize the session
		$session = curl_init($request);

		// Set curl options
		curl_setopt($session, CURLOPT_HEADER, false);
		curl_setopt($session, CURLOPT_RETURNTRANSFER, true);

		// Make the request
		$response = curl_exec($session);

		// Close the curl session
		curl_close($session);
//        var_dump($response);
//        error_log(print_r($response, true));
		$responseArray = unserialize($response);

		echo json_encode($responseArray['ResultSet']['Result']);

	}

}
?>
