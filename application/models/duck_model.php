<?php /**/ ?><?php

/*
 *  For this, we :
 *    Create the history record
 *    Mark the assignment in the duck record
 *    Create a "duck_assign" record
 *    Have that person start tracking that duck
 */

class Duck_model Extends CI_Model {

    function addHistory ( $duck_id, $user_id, $action_id, $datetime= null )
    {
        $ip = empty($_SERVER['REMOTE_ADDR']) ? @$REMOTE_ADDR : @$_SERVER['REMOTE_ADDR'];
//        error_log($ip);
        $data = array(
            'duck_id'   => $duck_id,
            'user_id'   => $user_id,
            'action_id' => $action_id,
            'user_ip'   => ip2long($ip),
        );

        if ( ! empty($datetime) ) {
            $data['timestamp'] = $datetime;
        }

        $this->db->insert('duck_history', $data);
        return $this->db->insert_id();
    }

    function assign( $duck_id, $user_id )
    {
        if (empty($user_id) || empty($duck_id)) {
            return;
        }

        //  Make sure this person isn't the current owner.  If they are, then don't do anything
        $this->db->select('duck_id')->from('duck')->where('current_owner_id', $user_id);
        if ($this->db->count_all_results()) {
            return;
        }

        //  Set the history
        $duck_history_id = $this->addHistory( $duck_id, $user_id, 3 );

        $data = array(
            'duck_id' => $duck_id,
            'user_id' => $user_id,
            'duck_history_id' => $duck_history_id,
        );
        $this->db->insert('duck_assign', $data);

        $data = array(
            'current_owner_id' => $user_id
        );
        $this->db->where('duck_id', $duck_id);
        $this->db->update('duck', $data);


        //  Start following duckie
        $this->track( $duck_id, $user_id );

    }

    function untrack( $duck_id, $user_id )
    {
        if (empty($user_id) || empty($duck_id)) {
            return;
        }

        $duck_history_id = $this->addHistory( $duck_id, $user_id, 6 );

        //		$this->db->select('duck_id')->from('duck_track')->where('user_id', $user_id)->where('duck_id', $duck_id);
        $this->db->delete('duck_track', array('user_id' => $user_id, 'duck_id' => $duck_id));

    }

    function track( $duck_id, $user_id )
    {
        if (empty($user_id) || empty($duck_id)) {
            return;
        }

        $duck_history_id = $this->addHistory( $duck_id, $user_id, 5 );

        $this->db->select('duck_id')->from('duck_track')->where('user_id', $user_id)->where('duck_id', $duck_id);

        //  This person is not tracking the duckie yet.
        if (! $this->db->count_all_results()) {
            $data = array(
                'user_id' => $user_id,
                'duck_id' => $duck_id,
                'duck_history_id' => $duck_history_id,
            );
            $this->db->insert('duck_track', $data);
        }

    }

    function addLocation( $duck_id, $user_id, $lat, $lon, $comments, $link_list, $date_time, $location, $approved )
    {
        $this->load->helper('duck');

        if (empty($duck_id)) {
            return null;
        }

        $date_time = $this->format_date_time($date_time);

        $duck_history_id = $this->addHistory( $duck_id, $user_id, 4, $date_time );

        $distance_to = $this->getDistanceTo( $lat, $lon, $duck_id );

        $duck_data = array(
            'duck_id'         => $duck_id,
            'user_id'         => $user_id,
            'duck_history_id' => $duck_history_id,
            //'link'            => $link,
            'latitude'        => $lat,
            'longitude'       => $lon,
            'comments'        => $comments,
            //'flickr_photo_id' => (empty ($flickr_photo_id) ? NULL : $flickr_photo_id ),
            'date_time'       => $date_time,
            'location'        => $location,
            'approved'        => $approved,
            'distance_to'     => $distance_to,
        );

        $this->db->insert('duck_location', $duck_data);
        $location_id = $this->db->insert_id();
		$duck_data['location_id'] = $location_id;
		
        //Add Links
        if (is_array($link_list)) {
            foreach ($link_list as $link) {
                if (!empty($link)) {
                    $link_data = array(
                        'duck_location_id' => $location_id,
                        'link' => $link,
                    );
                    $this->db->insert('duck_location_link', $link_data);
                }
            }
        }

        $total_distance = $this->getTotalDistance( $duck_id, $lat, $lon );
        $distance_data = array(
            'total_distance' => $total_distance
        );
        $this->db->where('duck_id', $duck_id);
        $this->db->update('duck', $distance_data);

        $this->mail_location_update_emails($duck_id, $location_id);

		if ($approved == 'Y'  && $location != 'Home') {
			$this->tweetNewLocation($duck_data);
		}
		
        return $location_id;
    }

    function updateLocation( $duck_location_id, $duck_id, $user_id, $lat, $lon, $comments, $links, $date_time, $location, $approved )
    {
        $this->load->helper('duck');

        if (empty($duck_id)) {
            return null;
        }

        $date_time = $this->format_date_time($date_time);

        $duck_history_id = $this->addHistory( $duck_id, $user_id, 7, $date_time );

        $distance_to = $this->getDistanceTo( $lat, $lon, $duck_id, $duck_location_id );

        $duck_data = array(
            'duck_id'         => $duck_id,
//            'user_id'         => $user_id,
            'duck_history_id' => $duck_history_id,
//            'link'            => $link,
            'latitude'        => $lat,
            'longitude'       => $lon,
            'comments'        => $comments,
//            'flickr_photo_id' => (empty ($flickr_photo_id) ? NULL : $flickr_photo_id ),
            'date_time'       => $date_time,
            'location'        => $location,
            'approved'        => $approved,
        );

        $this->db->where('duck_location_id', $duck_location_id);
        $this->db->update('duck_location', $duck_data);

        //Add Links
        $this->db->delete('duck_location_link', array('duck_location_id' => $duck_location_id));
        foreach ($links as $link) {
            if (!empty($link)) {
                $link_data = array(
                    'duck_location_id' => $duck_location_id,
                    'link' => $link,
                );
                $this->db->insert('duck_location_link', $link_data);
            }
        }

        $total_distance = $this->getTotalDistance( $duck_id );
        $distance_data = array(
            'total_distance' => $total_distance
        );
        $this->db->where('duck_id', $duck_id);
        $this->db->update('duck', $distance_data);

        $this->mail_location_update_emails($duck_id, $duck_location_id);

        return $duck_location_id;
    }



    function create( $duck_id, $current_owner_id, $name, $comments, $approved )
    {
        $data = array(
            'duck_id' => $duck_id,
            'current_owner_id' => $current_owner_id,
            'name' => empty($name) ? null : $name,
            'comments' => $comments,
        );

		if ($approved !== NULL) {
			$data['approved'] = $approved;
		}
		
        $this->db->insert('duck', $data);

        $this->addHistory($duck_id, 2, 1, '2008-08-16 13:30:00' );  //  User ID = 1.  Tommy

        $home_lat = '32.8466306766219';
        $home_lon = '-96.7279136180878';
        $this->addLocation( $duck_id, 2, $home_lat, $home_lon, 'Initial Creation', array(), '2008-08-22 20:00:00', 'Home', 'Y');

    }


    function createUnlessExists( $duck_id, $current_owner_id, $name, $comments, $approved = NULL )
    {
        $this->db->select('duck_id')->from('duck')->where('duck_id', $duck_id);

        if (!$this->db->count_all_results() ) {
            $this->create( $duck_id, $current_owner_id, $name, $comments, $approved );
        }
    }

    function isTracking( $duck_id, $user_id )
    {
        $this->db->select('duck_id')->from('duck_track')->where('user_id', $user_id)->where('duck_id', $duck_id);
        return  $this->db->count_all_results();

    }

    function getTotalDistance( $duck_id )
    {
        $this->load->helper('duck');

        $this->db->select('latitude, longitude')
			->from('duck_location')
				->where('duck_id', $duck_id)
				->where('approved', 'Y')
				->order_by('date_time', 'DESC');
        $query = $this->db->get();

        $result = $query->result_array();
        //		error_log(print_r($result, true));
        $distance = 0;
        if ( count($result) > 1 ) {
            $coord = array_shift($result);
            $lat1 = $coord['latitude'];
            $lon1 = $coord['longitude'];

            foreach ($result as $coord) {
                $jump_distance = distance($lat1, $lon1, $coord['latitude'], $coord['longitude']);
                $distance += $jump_distance;
                //				error_log("distance:  $lat1, $lon1 -> {$coord['latitude']}, {$coord['longitude']} = $jump_distance.  Total = $distance");
                $lat1 = $coord['latitude'];
                $lon1 = $coord['longitude'];
            }
        }
        return $distance;
    }

    function updateDuckLocationUserId( $location_id, $user_id )
    {
        $this->db->select('user_id')
			->from('duck_location')
				->where('duck_location_id', $location_id)
				->where('user_id', 0);

        if ($this->db->count_all_results() ) //  The Userid isn't set.  Assuming it's valid
        {
            $data = array(
                'user_id' => $user_id
            );
            $this->db->where('duck_location_id', $location_id);
            $this->db->update('duck_location', $data);
        }
    }

    function deleteLocation( $location_id )
    {
        if ( empty( $location_id ) ) {
            return FALSE;
        }

        //  Need to get the duck_id first
        $this->db->select('duck_id, duck_history_id')
        ->from('duck_location')
        ->where('duck_location_id', $location_id);
        $query = $this->db->get();
        $result = $query->result_array();
        $duck_id = $result[0]['duck_id'];
        $duck_history_id = $result[0]['duck_history_id'];

        $this->db->delete('duck_location', array('duck_location_id' => $location_id));
        $this->db->delete('duck_history', array('duck_history_id' => $duck_history_id));

        $total_distance = $this->getTotalDistance( $duck_id );
        $distance_data = array(
            'total_distance' => $total_distance
        );
        $this->db->where('duck_id', $duck_id);
        $this->db->update('duck', $distance_data);

        //  Now update the next location's distance_to field
        $this->db->select('duck_location_id, latitude, longitude')->from('duck_location')->where('duck_location_id >', $location_id)->where('duck_id', $duck_id)->order_by('date_time', 'DESC')->limit(1);
        $query = $this->db->get();

        if ($query->num_rows()) {
            $next_duck_info = $query->row_array();

            $this->db->select('latitude, longitude')->from('duck_location')->where('duck_location_id <', $location_id)->where('duck_id', $duck_id)->order_by('date_time', 'ASC')->limit(1);
            $query = $this->db->get();
            $prev_duck_info = $query->row_array();

            $next_distance_to = distance($prev_duck_info['latitude'], $prev_duck_info['longitude'], $next_duck_info['latitude'], $next_duck_info['longitude']);

            $distance_info = array( 'distance_to' => $next_distance_to);
            $this->db->where('duck_location_id', $next_duck_info['duck_location_id']);
            $this->db->update('duck_location', $distance_info);
        }
        //  Done updating next location's distance_to field

        return $duck_id;
    }

    function getLocationInfo( $location_id )
    {
        if ( empty( $location_id ) ) {
            return FALSE;
        }

        $sql = 'SELECT `duck_id`, `duck_history_id`, `user_id`, `latitude`, `longitude`, `comments`, `link`, `username`, '
        . ' `flickr_photo_id`, date_format(`date_time`, "%m/%d/%Y %T") as `date_time`, `location`, `distance_to`'
        . ' FROM `duck_location`'
        . ' LEFT JOIN `users` ON (`user_id`=`id`)'
        . ' WHERE `duck_location_id` = ? AND `approved`="Y"';
        $query = $this->db->query($sql, array($location_id));
        //		$this->db->select('duck_id, duck_history_id, user_id, latitude, longitude, comments, link, flickr_photo_id, date_format(date_time, "%m/%d/%Y %T") as date_time, location')->from('duck_location')->where('duck_location_id', $location_id);
        //        $query = $this->db->get();
        $result = $query->row_array();

        return $result;
    }

    function getInfo( $duck_id )
    {
        $this->db->select('name, username, comments, total_distance')
			->from('duck')
			->join('users', 'users.id=duck.current_owner_id', 'left')
			->where('duck_id', $duck_id)
			->where('approved', 'Y');
        $query = $this->db->get();

        if ($query->num_rows())
        {
            $duck_info = $query->row_array();
            $name_id = (empty($duck_info['name']) ? 'Unnamed '  : $duck_info['name']) . " ({$duck_id})";
            $duck_info['name_id'] = $name_id;
        }
        else
        {
            $duck_info = array();
        }

        return $duck_info;
    }

    function getLocationLinks( $location_id )
    {
        $this->db->select('link')
			->from('duck_location_link')
			->where('duck_location_id', $location_id);
        $query = $this->db->get();

        $links = array();
        if ($query->num_rows())
        {
            foreach ($query->result_array() as $row) {
                $links[] = $row['link'];
            }
        }
 
        return $links;
    }

    function getFullList()
    {
        $this->db->select('duck_id, name')
			->from('duck')
			->where('approved', 'Y')
			->order_by('duck_id');
        $query = $this->db->get();

        $duck_list = count($query->result_array()) ? array('' => '') : array();
        foreach ($query->result_array() as $row) {
            $name = (empty($row['name']) ? 'Unnamed '  : $row['name']) . " ({$row['duck_id']})";
            $duck_list[$row['duck_id']] = $name;
        }

        return $duck_list;
    }

    function getUserList( $user_id )
    {
        $this->db->select('duck.duck_id, name')
			->from('duck_track')
			->join('duck', 'duck.duck_id=duck_track.duck_id')
			->where('user_id', $user_id);
        $query = $this->db->get();

        $duck_list = count($query->result_array()) ? array('' => '') : array();
        foreach ($query->result_array() as $row) {
            $name = (empty($row['name']) ? 'Unnamed '  : $row['name']) . " ({$row['duck_id']})";
            $duck_list[$row['duck_id']] = $name;
        }

        return $duck_list;
    }

    function getLatestLocations()
    {
        $sql = 'SELECT * FROM '
                        . '(SELECT duck_id, duck_location_id, location, latitude, longitude, comments FROM duck_location'
                        . ' WHERE `approved`="Y" ORDER BY duck_id, duck_location_id DESC)'
                    . ' AS l GROUP BY duck_id, duck_location_id, location, latitude, longitude, comments';
        $query = $this->db->query($sql);
        //		$this->db->select('duck_id, duck_history_id, user_id, latitude, longitude, comments, link, flickr_photo_id, date_format(date_time, "%m/%d/%Y %T") as date_time, location')->from('duck_location')->where('duck_location_id', $location_id);
        //        $query = $this->db->get();

        $location_list = $query->result_array();
        //print_r($location_list);
        return $location_list;
    }

    function getAllLocations()
    {
        $this->db->select('duck_location.duck_id, name, duck_location_id, location, latitude, longitude, duck_location.comments, link, flickr_photo_id')
			->from('duck_location')
			->join('duck', 'duck_location.duck_id=duck.duck_id', 'left')
			->where('duck_location.approved', 'Y')
			->order_by('date_time', 'ASC');
        $query = $this->db->get();
        $location_list = $query->result_array();
        //print_r($location_list);
        return $location_list;

    }
    function getLocations( $duck_id )
    {
        $this->db->select('duck_location.duck_id, duck.name, duck_location_id, location, latitude, longitude, duck_location.comments, link, flickr_photo_id')
			->from('duck_location')
			->join('duck', 'duck_location.duck_id=duck.duck_id', 'left')
			->where('duck_location.duck_id', $duck_id)
			->where('duck_location.approved', 'Y')
			->order_by('date_time', 'ASC');
        $query = $this->db->get();
        $location_list = $query->result_array();
        //print_r($location_list);
        return $location_list;
    }

    function getLocation( $duck_location_id )
    {
        $this->db->select('latitude, longitude, comments, link, flickr_photo_id')
			->from('duck_location')
			->where('approved', 'Y')
			->where('duck_location_id', $duck_location_id)
			->limit(1);
        $query = $this->db->get();
        $location_list = $query->row_array();
        return $location_list;
    }

    function renderLocation( $location )
    {
        $textbox = empty($location['comments']) ? '' : htmlentities($location['comments'], ENT_QUOTES);
        $link = empty($location['link']) ? '' : "<a href=\"{$location['link']}\" target=\"_blank\">Link</a>";
        $textbox .= empty($link) ? '' : ( empty($textbox) ? $link : " <br><br> {$link}" );

        if (!empty($location['thumbnail_url'])) {
            $textbox = "<img src=\"{$location['thumbnail_url']}\" /><br/>" . $textbox;
        }

        $location['textbox'] = empty($textbox) ? "No Data" : $textbox;
        //$data['duck_location'][] = $location;
        return $location;
    }

    function canModifyLocation( $location_id )
    {
        if ( $this->dx_auth->get_role_id() == 2 ) {
            return true;
        }

        $location_info = $this->duck->getLocationInfo( $location_id );
        if ( $this->dx_auth->get_user_id() == $location_info['user_id'] ) {
            return true;
        }

        return false;
    }

    private function format_date_time( $date_time )
    {
        if (preg_match("/^(\d{1,2})\/(\d{1,2})\/(\d{2,4}) ([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/", $date_time, $matches) ) {
//            			error_log("sec" . print_r($matches, true));
            $date_time = "{$matches[3]}/{$matches[1]}/{$matches[2]} {$matches[4]}:{$matches[5]}:{$matches[6]}";
        }
//        if (preg_match("/^(\d{1,2})\/(\d{1,2})\/(\d{2,4}) ([01][0-9]|2[0-3]):([0-5][0-9])$/", $date_time, $matches) ) {
//            			error_log("sec" . print_r($matches, true));
//            $date_time = "{$matches[3]}/{$matches[1]}/{$matches[2]} {$matches[4]}:{$matches[5]}";
//        }
        elseif (preg_match("/(\d{1,2})\/(\d{1,2})\/(\d{2,4})/", $date_time, $matches) ) {
            			error_log("nosec:" . print_r($matches, true));
            $date_time = "{$matches[3]}/{$matches[1]}/{$matches[2]}";
        }

        return $date_time;
    }

    function mail_location_update_emails( $duck_id, $duck_data )
    {
//        if (!$this->config->item('send_emails')) {
//            return;
//        }

        //  Notify Tommy
        send_duck_location_change_mail('snoopykiss@gmail.com', $duck_id, $duck_data);

        //  Now we notify everyone who's on the track list
        $this->db->select('email')->from('duck_track')->join('users', 'duck_track.user_id=users.id')->where('duck_id', $duck_id);
        $query = $this->db->get();
        $result = $query->result_array();
        foreach ($result as $user_data) {
            send_duck_location_change_mail($user_data['email'], $duck_id, $duck_data);
        }

    }

    function getDistanceTo($lat, $lon, $duck_id, $duck_location_id = NULL)
    {
        $this->load->helper('duck');

        //select latitude, longitude from duck_location where duck_id=972 and duck_location_id < 34 order by duck_location_id desc limit 1;

        if (empty($duck_location_id)) {
            $this->db->select('duck_location_id, latitude, longitude')
            ->from('duck_location')
            ->where('duck_id', $duck_id)
            ->order_by('duck_location_id', 'desc')
            ->limit(1);
        } else {
            $this->db->select('duck_location_id, latitude, longitude')
            ->from('duck_location')
            ->where('duck_id', $duck_id)
            ->where('duck_location_id <', $duck_location_id)
			->where('approved', 'Y')
            ->order_by('duck_location_id', 'desc')
            ->limit(1);
        }

        $query = $this->db->get();

        if ($query->num_rows()) {
            $result = $query->row_array();
            //            print_r($result);
            //            print "lat = $lat, $lon = $lon";
            $distance_to = (float) distance($result['latitude'], $result['longitude'], $lat, $lon);

        }
        else {
            $distance_to = 0;
        }
        return $distance_to;
    }

    function isRenamable($duck_id)
    {
        $duck_info = $this->getInfo($duck_id);

        $result = FALSE;
        if (!empty($duck_info) && empty($duck_info['name'])) {
            $result = TRUE;
        }

        return $result;
    }

    function isNameTaken($name)
    {
        $this->db->select('name')->from('duck')->where('name', $name);
        $query = $this->db->get();

        if ($query->num_rows()) {
            return TRUE;
        }
        else {
            return FALSE;
        }
    }

	function tweetNewLocation($data)
	{
		if ($this->config->item('send_tweets'))
		{
				$this->load->library('tweet');
				$this->tweet->enable_debug(TRUE);
				$tokens = array(
					'oauth_token'        => $this->config->item('oauth_token'),
					'oauth_token_secret' => $this->config->item('oauth_token_secret')
				);
				 $this->tweet->set_tokens($tokens);

				if ( $this->tweet->logged_in() )
				{
					$this->tweet->call('post', 'statuses/update', array('status' => "Duck #{$data['duck_id']} has just moved to \"{$data['location']}\" http://duckiehunt.com/view/location/{$data['location_id']}"));
				}
		}
	}

	function addActivity($user_agent, $action, $client_ip, $duck_id, $location, $comments)
	{
        $activity_data = array(
            'user_agent'         => $user_agent,
			'action' => $action,
			'client_ip' => $client_ip,
			'duck_id' => $duck_id,
			'location' => $location,
			'comments' => $comments,
        );

        $this->db->insert('activity', $activity_data);
	}
}
?>
