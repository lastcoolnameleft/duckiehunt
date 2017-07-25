<?php

class View extends CI_Controller {


	function index()
	{
		$this->duck();
	}

	function duck( $duck_id = 0 )
	{
        $this->load->model('duck_model', 'duck');

        $duck_info = $this->duck->getInfo($duck_id);
		$user_id = $this->ion_auth->get_user_id();
		
        $data = array(
            'duck_info'       => $duck_info,
            'base_url'        => $this->config->item('base_url'),
            'duck_id'         => $duck_id,
            'user_id'         => $user_id,
            'is_tracking'     => $this->duck->isTracking($duck_id, $user_id),
            'user_duck_list'  => $this->duck->getUserList($user_id),
            'total_duck_list' => $this->duck->getFullList(),
        );

        $map_data = array(
            'focus_lat' => 0,
            'focus_long' => 0,
            'focus_zoom' => 2,
            'location_list' => array(),
        );

        if (empty($duck_info)) {
            $this->load->view('header');
            $this->load->view('duck/view/dropdown', $data);
            $this->load->view('footer');
            return;
        }


        $duck_location_id = 0;
		//  Duck Locations
		if ( !empty($duck_id) ) {
			$location_list = $this->duck->getLocations( $duck_id );
            $map_data['location_list'] = $location_list;
            $data['location_list'] = array();
            $data['duck_location_pulldown'] = array();

			$this->load->library('flickr');

            if (!empty($location_list)) { 
                $data['duck_location_pulldown'][''] = '';
                $data['duck_location_list'] = $location_list;
            }

			foreach ($location_list as $location) {
                $data['duck_location_pulldown'][$location['duck_location_id']] = $location['location'];

                if (!empty($location['flickr_photo_id'])) {
                    $location['thumbnail_url'] = $this->flickr->getThumbnail($location['flickr_photo_id']);
                }
                $data['location_list'][] = $this->duck->renderLocation( $location );
			}
		}
        
        $data['duck_location_id'] = $duck_location_id;
		$this->load->view('header');
        $this->load->view('duck/view/dropdown', $data);
		$this->load->view('duck/view/duck', $data);
        $this->load->view('duck/view/map', $map_data);
		$this->load->view('footer');
	}
    
	function location( $duck_location_id = 0 )
	{
        $this->load->model('duck_model', 'duck');

        $location_info = $this->duck->getLocationInfo($duck_location_id);

        if (empty($location_info['duck_id'])) {
            $this->load->view('header');
            $this->load->view('duck/view/not_found');
            $this->load->view('footer');
            return;
        }
        
        $duck_id = $location_info['duck_id'];
		$user_id = $this->ion_auth->get_user_id();
		
        $data = array(
            'duck_location_id' => $duck_location_id,
            'location_info'    => $this->duck->getLocationInfo($duck_location_id),
            'duck_info'        => $this->duck->getInfo($duck_id),
            'base_url'         => $this->config->item('base_url'),
            'duck_id'          => $duck_id,
            'user_id'          => $user_id,
            'is_tracking'      => $this->duck->isTracking($duck_id, $user_id),
            'user_duck_list'   => $this->duck->getUserList($user_id),
            'total_duck_list'  => $this->duck->getFullList(),
            'can_modify'       => $this->duck->canModifyLocation($duck_location_id),
            'links'            => $this->duck->getLocationLinks($duck_location_id),
        );

        $map_data = array(
            'focus_lat'        => 0,
            'focus_long'       => 0,
            'focus_zoom'       => 2,
            'location_list'    => array(),
            'duck_location_id' => $duck_location_id
        );

		//  Duck Locations
		if ( !empty($duck_id) ) {
			$location = $this->duck->getLocation( $duck_location_id );

            $this->load->library('flickr');
            
            if (!empty($location['flickr_photo_id'])) {
                $location['thumbnail_url'] = $this->flickr->getThumbnail($location['flickr_photo_id']);
            }

            if (!empty($location['flickr_photo_id'])) {
                $data['location_info']['flickr_photo_info'] = $this->flickr->getPhotoInfo($location['flickr_photo_id']);
            }
//            print "page = $flickr_photo_page";
               
            $data['location_list'][] = $this->duck->renderLocation( $location );

			$location_list = $this->duck->getLocations( $duck_id );
            $map_data['location_list'] = $location_list;

            $data['duck_location_pulldown'] = array();

            if (!empty($location_list)) { $data['duck_location_pulldown'][''] = ''; }
			foreach ($location_list as $location) {
                $data['duck_location_pulldown'][$location['duck_location_id']] = $location['location'];
			}
		}
        $data['duck_location_id'] = $duck_location_id;

		$this->load->view('header');
        $this->load->view('duck/view/dropdown', $data);
		$this->load->view('duck/view/location', $data);
        $this->load->view('duck/view/map', $map_data);
		$this->load->view('footer');
	}


    function alert( $duck_id, $action = 'add' )
    {
        $user_id = $this->ion_auth->get_user_id();
        $this->load->model('duck_model', 'duck');

        $this->load->view('header');

		if ( $action == 'remove')  {
	        $this->duck->untrack( $duck_id, $user_id );
			$this->load->view('alert/success');
		}
		elseif ( $action === 'add' ) {
		}
		else {
	        $this->load->view('alert/fail');
		}
	
        $this->load->view('footer');
    }


	function add_alert() 
	{
        $user_id = $this->ion_auth->get_user_id();
		$duck_id = $this->input->post('duck_id');

        $this->load->model('duck_model', 'duck');
	
        $this->load->view('header');
//			$this->ion_auth->check_uri_permissions();
	        $this->duck->track( $duck_id, $user_id );
	        $this->load->view('alert/success');
	}
}
?>
