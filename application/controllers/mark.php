<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Mark extends CI_Controller 
{

	private $_approved = 'Y';
	
    function __construct()
    {
        parent::__construct();

        $this->load->helper(array('form', 'url'));
        $this->load->library('form_validation');
        $this->load->model('duck_model', 'duck');

        $this->form_validation->set_rules('duck_id', 'Duck ID', 'trim|required|numeric|callback_duck_id_check');
        $this->form_validation->set_rules('date_time', 'Date & Time', 'trim|required');
        $this->form_validation->set_rules('lat', 'Latitude', 'trim|required|numeric|callback_latlng_check');
        $this->form_validation->set_rules('lng', 'Longtitude', 'trim|required|numeric|callback_latlng_check');
        $this->form_validation->set_rules('comments', 'Comments', 'xss_clean');
        $this->form_validation->set_rules('location', 'Central Location', 'trim|required');

        for ($i=0; $i<10; $i++) {
            $link = $this->input->post('link' . $i);
            if (!empty($link)) {
                $this->form_validation->set_rules('link' . $i, $link, 'xss_clean|valid_url');
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
            'controller' => 'mark',
        );

        if ($this->form_validation->run() == FALSE) {
            $this->load->view('header');
            $this->load->view('duck/mark/mark_main', $data);
            $this->load->view('duck/mark/map');
            $this->load->view('footer');
        }
        else {
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
            'duck_location_id' => $duck_location_id,
            'location_info'    => $location_info,
            'controller'       => "mark/update/{$duck_location_id}",
            'links'            => $links,
        );

        if (!$this->duck->canModifyLocation( $duck_location_id )) {
            $this->load->view('header');
            $this->load->view('duck/mark/denied');
            $this->load->view('footer');
        }
        else {
//            $this->dx_auth->check();

            $location_info = $this->duck->getLocationInfo($duck_location_id);

            if ($this->form_validation->run() == FALSE) {
                $this->load->view('header');
                $this->load->view('duck/mark/mark_main', $data);
                $this->load->view('duck/mark/map');
                $this->load->view('footer');
            }
            else {
                $this->_update( $duck_location_id );
            }
        }
    }

    function duck_id_check( $duck_id )
    {
        if (!is_numeric($duck_id))
        {
            $this->form_validation->set_message('duck_id_check', 'The %s field must be a number');
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
            $this->form_validation->set_message('latlng_check', 'Invalid %s');
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

        $cl_user_id = $this->dx_auth->get_user_id();
        $this->duck->createUnlessExists(
            $duck_id,
            $cl_user_id,
            '',
            '',
			$this->_approved
        );

        $link_list = $this->_uploadFile($duck_id, $this->input->post('comments'));
        for ($i=0; $i<10; $i++) {
            $link = $this->input->post('link' . $i);
            if (!empty($link)) {
                $link_list[] = $this->input->post('link' . $i);
            }
        }

        $duck_id = $this->input->post('duck_id');
        $location_id = $this->duck->addLocation(
            $duck_id,
            2, // $cl_user_id, //TODO: Fix this
            $this->input->post('lat'),
            $this->input->post('lng'),
            $this->input->post('comments'),
            $link_list,
            $this->input->post('date_time'),
            $this->input->post('location'),
            $this->_approved
        );

        $this->session->set_userdata('modifying_duck', $duck_id);
        $this->session->set_userdata('location_id', $location_id);

        $this->load->view('header');

		if ($this->_approved == 'Y') {
	        $this->load->view('duck/mark/success', array('location_id' => $location_id));
		}
		else {
	        $this->load->view('duck/mark/success_not_approved', array('location_id' => $location_id));
		}

        if ($this->duck->isRenamable($duck_id)) {
            $this->load->view('duck/mark/not_named', array('duck_id' => $duck_id));
        }

        if (!$this->dx_auth->is_logged_in() ) {
            $this->load->view('duck/mark/not_reg');
        }

        $this->load->view('footer');
    }


    private function _update( $duck_location_id )
    {
        $cl_user_id = $this->dx_auth->get_user_id();
        $duck_id = $this->input->post('duck_id');
        
        $this->session->set_userdata('modifying_duck', $duck_id);

        $link_list = $this->_uploadFile($duck_id, $this->input->post('comments'));
        for ($i=0; $i<10; $i++) {
            $link = $this->input->post('link' . $i);
            if (!empty($link)) {
                $link_list[] = $this->input->post('link' . $i);
            }
        }

        $location_id = $this->duck->updateLocation(
            $duck_location_id,
            $duck_id,
            $cl_user_id,
            $this->input->post('lat'),
            $this->input->post('lng'),
            $this->input->post('comments'),
            $link_list,
            $this->input->post('date_time'),
            $this->input->post('location'),
            'Y' //  Approved
        );

        $this->load->view('header');
        $success_data = array('location_id' => $duck_location_id);
        $this->load->view('duck/mark/update_success', $success_data);

        if ($this->duck->isRenamable($duck_id)) {
            $this->load->view('duck/mark/not_named', array('duck_id' => $duck_id));
        }

        if (!$this->dx_auth->is_logged_in() ) {
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
        
        if ($this->duck->isRenamable($duck_id)) {
            if ($this->isValidName($name)) {
                if (!$this->duck->isNameTaken($name)) {
                    if ($this->session->userdata('modifying_duck') == $duck_id) {

                        $data = array('name' => $name);
                        $this->db->where('duck_id', $duck_id);
                        $this->db->update('duck', $data);

                        $result = array('status' => 'success', 'message' => 'Name Updated!');
                    } else {
                        $result = array('status' => 'failure', 'message' => 'You don\'t have permission to update');
                    }
                } else {
                    $result = array('status' => 'failure', 'message' => 'Sorry, but that name is already taken');
                }
            } else {
                $result = array('status' => 'failure', 'message' => 'Invalid Name');
            }
        } else {
            $result = array('status' => 'failure', 'message' => 'This duck has already been named');
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
    

    function _uploadFile($duck_id, $desc)
    {
        $result = array();
        $config['upload_path'] = './uploads/'; // server directory
        $config['allowed_types'] = 'gif|jpg|png'; // by extension, will check for whether it is an image

        $this->load->library('upload', $config);

        if ( $this->upload->do_upload('userfile')) {
            $data = $this->upload->data();
            error_log('File upload successful');
        } else {
            error_log('Either file upload unsuccessful or no file uploaded');
        }
        return ;

        if ( ! $files )
        {
            $error = array('error' => $this->upload->display_errors());
        }
        else
        {
            $data = array('upload_data' => $files);

            $this->load->library('Flickr_API');
            $data = array('upload_data' => $files);
            $token = getenv('FLICKR_TOKEN');
            $secrets = array(
                'api_key'=> getenv('FLICKR_API_KEY'),
                'api_secret' => getenv('FLICKR_API_SECRET'));
            $flickr = new Flickr($secrets);
            $flickr->token = $token;

            $flickr->token = $token;
            error_log(print_r($data, true));
            foreach ($data['upload_data'] as $pic) {
                $title = 'Duck #' . $duck_id;
                $pic_desc = $desc . "<br/>\n" . anchor("http://duckiehunt.com/view/duck/{$duck_id}");
                $tags  = "duckiehunt,rubber duckie,duckie,{$duck_id}";
                $perms = array("is_public"=>1);
                $async = FALSE;

                $photo_id = $flickr->upload($pic['file'], $title, $pic_desc, $tags, $perms, $async);
                $photo = $flickr->photosGetInfo($photo_id);
                $result[] = $photo['urls']['photopage'];
            }
        }

        return $result;
    }
}

?>
