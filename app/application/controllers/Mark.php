<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Mark extends CI_Controller 
{

	private $_approved;
	
    function __construct()
    {
        parent::__construct();

        $this->load->helper(array('form', 'url'));
        $this->load->library(array('form_validation', 'sendgrid', 'recaptcha'));
        $this->load->model('duck_model', 'duck');
        $this->_approved = $this->config->item('auto_approve');

        if ( ! $this->ion_auth->logged_in() ) {
            $this->load->helper('cookie');
            $cookie = array(
                'name'   => 'auth_redirect',
                'value'  => '/mark',
                'expire' => '600',
                'prefix' => ''
             );
            $this->input->set_cookie($cookie);
            redirect('/auth');
        }

        $this->form_validation->set_rules('duck_id', 'Duck ID', 'trim|required|numeric|callback_duck_id_check');
        $this->form_validation->set_rules('date_time', 'Date & Time', 'trim|required');
        $this->form_validation->set_rules('lat', 'Latitude', 'trim|required|numeric|callback_latlng_check');
        $this->form_validation->set_rules('lng', 'Longtitude', 'trim|required|numeric|callback_latlng_check');
        $this->form_validation->set_rules('location', 'Central Location', 'trim|required');
        $this->form_validation->set_rules('g-recaptcha-response', 'Captcha', 'required');

        for ($i=0; $i<10; $i++) {
            $link = $this->input->post('link' . $i);
            if (!empty($link)) {
                $this->form_validation->set_rules('link' . $i, $link, 'valid_url');
            }
        }

    }

    function index()
    {
        $data = array(
            'location_info' => array('duck_id' => '', 'duck_history_id' => '', 'user_id' => '', 'latitude' => '',
                'longtitude' => '', 'comments' => '', 'links' => '', 'flickr_photo_id' => '', 'date_time' => date('m/d/Y H:i:s'),
                'location' => ''
            ),
            'duck_id' => '',
            'name' => '',
            'location' => '',
            'lat' => '',
            'lng' => '',
            'links' => array(),
            'date_time' => date('m/d/Y H:i:s'),
            'comments' => '',
            'controller' => 'mark',
            'recaptcha_widget' => $this->recaptcha->getWidget(),
            'recaptcha_script' => $this->recaptcha->getScriptTag(),
        );

        if ($this->form_validation->run() == FALSE) {
            $this->load->view('header');
            $this->load->view('duck/mark/mark_main', $data);
            $this->load->view('duck/mark/map');
            $this->load->view('footer');
        }
        else {
            $recaptcha = $this->input->post('g-recaptcha-response');
            $response = $this->recaptcha->verifyResponse($recaptcha);
            if (!isset($response['success']) or !$response['success'] === true) {
                error_log('recapcha was not successful!');
                error_log(print_r($response, true));
                $this->load->view('header');
                $this->load->view('error', array('error_msg' => 'Recaptcha failed'));
                $this->load->view('footer');
                return;
            }
            $this->_add();
        }
    }


    function update( $duck_location_id )
    {
        $location_info = $this->duck->getLocationInfo($duck_location_id);

        $links = array();
        for ($i=0; $i<10; $i++) {
            $link = $this->input->post('link' . $i);
            if (!empty($link)) {
                $links[] = $link;
            }
        }
        if (empty($links)) {
            $links = $this->duck->getLocationLinks($duck_location_id);
        }

        $data = array(
            'duck_id'          => $location_info['duck_id'],
            'location'         => $location_info['location'],
            'comments'         => $location_info['comments'],
            'date_time'        => $location_info['date_time'],
            'lat'              => $location_info['latitude'],
            'lng'              => $location_info['longitude'],
            'duck_location_id' => $duck_location_id,
            'location_info'    => $location_info,
            'controller'       => "mark/update/{$duck_location_id}",
            'links'            => $links,
            'recaptcha_widget' => $this->recaptcha->getWidget(),
            'recaptcha_script' => $this->recaptcha->getScriptTag(),
        );

        if (!$this->duck->canModifyLocation( $duck_location_id )) {
            $this->load->view('header');
            $this->load->view('duck/mark/denied');
            $this->load->view('footer');
        }
        else {
            if ($this->form_validation->run() == FALSE) {
                $this->load->view('header');
                $this->load->view('duck/mark/mark_main', $data);
                $this->load->view('duck/mark/map');
                $this->load->view('footer');
            }
            else {
                $recaptcha = $this->input->post('g-recaptcha-response');
                $response = $this->recaptcha->verifyResponse($recaptcha);
                if (!isset($response['success']) or !$response['success'] === true) {
                    error_log('recapcha was not successful!');
                    error_log(print_r($response, true));
                    $this->load->view('header');
                    $this->load->view('error', array('error_msg' => 'Recaptcha failed'));
                    $this->load->view('footer');
                    return;
                }

                $this->_update( $duck_location_id );
            }
        }
    }

    function duck_id_check( $duck_id )
    {
        if (!is_numeric($duck_id))
        {
            $this->form_validation->set_message('duck_id_check', "The %s field must be a number.  Value: $duck_id");
            return FALSE;
        }
        else
        {
            return TRUE;
        }
    }

    function latlng_check( $latlng )
    {
        if (empty($latlng) )
        {
            $this->form_validation->set_message('latlng_check', "Invalid %s. Value: $latlng");
            return FALSE;
        }
        else
        {
            return TRUE;
        }
    }

    private function _add()
    {
        $duck_id = $this->input->post('duck_id');

		//  For keeping track of anyone malicious
		$this->duck->addActivity($this->input->user_agent(), 'add', $this->input->ip_address(), $duck_id, $this->input->post('location'), $this->input->post('comments'));

        $user_id = $this->ion_auth->get_user_id() ? $this->ion_auth->get_user_id() : 0;
        $this->duck->createUnlessExists(
            $duck_id,
            $user_id,
            '',
            '',
			$this->_approved
        );

        $links = $this->getLinks();

        $duck_id = $this->input->post('duck_id');
        $location_id = (int) $this->duck->addLocation(
            $duck_id,
            $user_id,
            $this->input->post('lat'),
            $this->input->post('lng'),
            $this->input->post('comments'),
            $links,
            $this->input->post('date_time'),
            $this->input->post('location'),
            $this->_approved
        );

        $this->_uploadFiles($duck_id, $location_id, $this->input->post('comments'));

        $this->config->load('duckiehunt');
        $notify_email = $this->config->item('notify_email');
        if ($notify_email) {
            $this->sendgrid->send_duck_location_change($notify_email, $duck_id, $location_id);
        }

        $this->session->set_userdata('modifying_duck', $duck_id);
        $this->session->set_userdata('location_id', $location_id);

		if ($this->_approved == 'Y') {
            $url = "/view/location/{$location_id}";
            redirect($url);
		}
		else {
            $this->load->view('header');
	        $this->load->view('duck/mark/success_not_approved', array('location_id' => $location_id));
            $this->load->view('footer');
		}

#        if ($this->duck->isRenamable($duck_id)) {
#            $this->load->view('duck/mark/not_named', array('duck_id' => $duck_id));
#        }

    }


    private function getLinks() {
        $link_list = array();
        for ($i=0; $i<10; $i++) {
            $link = $this->input->post('link' . $i);
            if (!empty($link)) {
                $link_list[] = $link;
            }
        }
        return $link_list;
    }

    private function _update( $duck_location_id )
    {
        $user_id = $this->ion_auth->get_user_id() ? $this->ion_auth->get_user_id() : 0;
        $duck_id = $this->input->post('duck_id');
        
        $this->session->set_userdata('modifying_duck', $duck_id);

        $links = $this->getLinks();

        $location_id = $this->duck->updateLocation(
            $duck_location_id,
            $duck_id,
            $user_id,
            $this->input->post('lat'),
            $this->input->post('lng'),
            $this->input->post('comments'),
            $links,
            $this->input->post('date_time'),
            $this->input->post('location'),
            'Y' //  Approved
        );

        $this->_uploadFiles($duck_id, $location_id, $this->input->post('comments'));


        $this->load->view('header');
        $success_data = array('location_id' => $duck_location_id);
        $this->load->view('duck/mark/update_success', $success_data);

        if ($this->duck->isRenamable($duck_id)) {
            $this->load->view('duck/mark/not_named', array('duck_id' => $duck_id));
        }

        if (!$this->ion_auth->logged_in() ) {
            $this->load->view('duck/mark/not_reg');
        }

        $this->load->view('footer');
    }

    function name($duck_id)
    {
//        $this->session->set_userdata('modifying_duck', $duck_id);
        $this->load->view('header');
        if ($this->duck->isRenamable($duck_id)) {
            $data = array('duck_id' => $duck_id);
            $this->load->view('duck/mark/not_named', $data);
        }
        $this->load->view('footer');
    }

    function setName($duck_id)
    {
        $name = $this->input->post('name');
        $user_id = $this->ion_auth->get_user_id() ? $this->ion_auth->get_user_id() : 0;
        if ($this->duck->isRenamable($duck_id, $user_id)) {
            if ($this->isValidName($name)) {
                if (!$this->duck->isNameTaken($name)) {
                    if ($this->session->userdata('modifying_duck') == $duck_id) {

                        $data = array('name' => $name);
                        $this->db->where('duck_id', $duck_id);
                        $this->db->update('duck', $data);

                        $result = array('status' => 'success', 'message' => 'Name Updated!');
                    } else {
                        $result = array('status' => 'failure', 'message' => 'You do not have permission to update');
                    }
                } else {
                    $result = array('status' => 'failure', 'message' => 'Sorry, but that name is already taken');
                }
            } else {
                $result = array('status' => 'failure', 'message' => 'Invalid Name');
            }
        } else {
            $result = array('status' => 'failure', 'message' => 'You are unable to name this duck');
        }

        print json_encode($result);
    }
    

    function isValidName($name)
    {
        $result = true;

        if (empty($name)) {
            $result = false;
        }

        $pattern = '/fuck|dick|d1ck|pussy|pu55y|jesus|shit|sh1t|cunt|fart/';
        if (preg_match($pattern, $name)) {
            $result = false;
        }

        return $result;
    }
    

    function _uploadFiles($duck_id, $duck_location_id, $desc)
    {
        $this->config->load('duckiehunt');
        $config['upload_path'] = $this->config->item('upload_path');
        $config['allowed_types'] = 'gif|jpg|jpeg|png'; // by extension, will check for whether it is an image

        $this->load->library('upload', $config);
        $upload_data = $this->upload->do_multi_upload("files");

        if ( $upload_data )
        {
            $flickr_config = array(
                'consumer_key' => $this->config->item('flickr_api_key'),//getenv('FLICKR_API_KEY'),
                'consumer_secret' => $this->config->item('flickr_api_secret'),//getenv('FLICKR_API_SECRET')
            );

            $this->config->load('duckiehunt');
            $this->load->library('Flickr', $flickr_config);
            $this->flickr->setOauthData('oauth_access_token', $this->config->item('flickr_access_token'));
            $this->flickr->setOauthData('oauth_access_token_secret', $this->config->item('flickr_access_token_secret'));
            $this->flickr->setOauthData('user_nsid', $this->config->item('flickr_user_nsid'));
            $this->flickr->setOauthData('user_name', $this->config->item('flickr_user_name'));
            $this->flickr->setOauthData('permissions', $this->config->item('flickr_permissions'));

            if (!$this->flickr->authenticate('write')) {
                error_log('unable to authenticate with Flickr');
            }

            foreach ($upload_data as $idx => $pic) {
                $title = 'Duck #' . $duck_id;
                $pic_desc = $desc . "<br/>\n" . anchor("http://duckiehunt.com/view/duck/{$duck_id}");
                $tags  = "duckiehunt,rubber duckie,duckie,duck{$duck_id}";
                $async = FALSE;
                # https://www.flickr.com/services/api/upload.api.html
                $parameters = array(
                    'title' => $title,
                    'tags' => $tags,
                    'description' => $pic_desc,
                    'photo' => curl_file_create($pic['full_path']),
                    'is_public' => $this->config->item('flickr_upload_is_public'),
                    'hidden' => $this->config->item('flickr_upload_hidden'),
                );

                $photo_info = $this->flickr->upload($parameters);
                error_log(print_r($photo_info, true));

                if (!$photo_info || $photo_info['stat'] === 'fail') {
                    error_log('Received an error uploading to Flickr');
                    $error_code = $this->flickr->error_code;
                    $error_msg = $this->flickr->error_msg;
                    error_log('Error Code:' . $error_code);
                    error_log('Error Msg:' . $error_msg);
                    return;
                }

                $flickr_photo_id = $photo_info['photoid']['_content'];
                $upload_data[$idx]['flickr_photo_id'] = $flickr_photo_id;
                $thumbnail_url = $this->flickr->getThumbnailUrl($flickr_photo_id);
                $this->duck->addLocationPhoto($duck_location_id, $flickr_photo_id, $thumbnail_url);
            }
        } else  {
            error_log('Received an error uploading photo locally');
            error_log('Error:' . $this->upload->display_errors());
        }

        return $upload_data;
    }
}

?>
