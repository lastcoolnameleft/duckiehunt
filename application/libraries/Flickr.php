<?php

class Flickr_API {
    private $_cfg = array('format' => 'php_serial');

    function __construct($params = array()) {
        $this->_cfg['api_key'] = getenv('FLICKR_API_KEY');
        $this->_cfg['api_secret'] = getenv('FLICKR_API_SECRET');

        if(isset($params['token'])) $this->token = $params['token'];
        foreach($params as $k => $v) {
            $this->_cfg[$k] = $v;
        }
        if(!$this->_cfg['api_key'] || !$this->_cfg['api_secret']) {
            throw new Exception("You must supply an api_key and an api_secret");
        }
    }

    function callMethod($params = array()) {
        $this->_err_code = 0;
        $this->_err_msg = '';

		$encoded_params = array();

		foreach ($this->_cfg as $k => $v){
			$encoded_params[] = urlencode($k).'='.urlencode($v);
		}

		foreach ($params as $k => $v){
			$encoded_params[] = urlencode($k).'='.urlencode($v);
		}

		$url = "http://api.flickr.com/services/rest/?".implode('&', $encoded_params);
		$ch = curl_init();
		$timeout = 5; // set to zero for no timeout
		curl_setopt($ch, CURLOPT_URL, $url);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
		$response = curl_exec($ch);

		$rsp_obj = unserialize($response);

        if (curl_errno($ch)) {
            throw new Exception(curl_error($ch));
        }

        curl_close($ch);
//        file_put_contents('/tmp/curl.log',print_r($params,true)."\n".$this->_http_body."\n\n",FILE_APPEND);

        $result = unserialize($response);
        return $result;
    }

    function getErrorCode() {
        return $this->_err_code;
    }

    function getErrorMessage() {
        return $this->_err_msg;
    }

    function showError() {
        echo "<br />ErrorCode: {$this->_err_code}<br />ErrorMessage: {$this->_err_msg}<br />\n";
    }

    function getAuthUrl($perms, $frob='') {
        $args = array('api_key'=>$this->_cfg['api_key'],'perms'=>$perms);

        if (strlen($frob)) { $args['frob'] = $frob; }

        $args['api_sig'] = $this->signArgs($args);

        $fields =  '';
        foreach($args as $k => $v) {
            if($fields) $fields.='&';
            $fields .= urlencode($k).'='.urlencode($v);
        }

        return $this->_cfg['auth_endpoint'].$fields;
    }


    function signArgs($args){
        ksort($args);
        $a = '';
        foreach($args as $k => $v) {
            $a .= $k . $v;
        }
        return md5($this->_cfg['api_secret'].$a);
    }
}

class Flickr extends Flickr_API {
    function __construct($params = array()) {
        parent::__construct($params);
    }

	function getThumbnail( $photo_id )
	{
		$params = array(
            'method'    => 'flickr.photos.getSizes',
			'photo_id'  => $photo_id,
		);

        $rsp_obj = $this->callMethod($params);

//        $result = array();
		if ($rsp_obj['stat'] == 'ok'){
			$result = $rsp_obj['sizes']['size']['0']['source'];
		}

		return $result;
	}

	function getPhotoInfo( $photo_id )
	{
		$params = array(
            'method'    => 'flickr.photos.getInfo',
			'photo_id'  => $photo_id,
		);

        $rsp_obj = $this->callMethod($params);

        $result = array();
		if ($rsp_obj['stat'] == 'ok'){
			$result['page'] = $rsp_obj['photo']['urls']['url']['0']['_content'];
			$result['title'] = $rsp_obj['photo']['title']['_content'];
		}

//        print_r($rsp_obj);
		return $result;
	}

    function upload( $photo, $title='', $description='', $tags='', $perms='', $async=1, $info=NULL) {
        $tmpf = false;
//        $params = array('auth_token'  => $this->token);
        $params = array(
            'method' => 'upload'
        );
        $url = parse_url($photo);
        if(isset($url['scheme'])) {
            $stream = fopen($photo,'r');
            $tmpf = tempnam('/var/tmp','G2F');
            file_put_contents($tmpf, $stream);
            fclose($stream);
            $params['photo'] = $tmpf;
        } else $params['photo'] = $photo;
        $info = filesize($params['photo']);
        if($title)       $params['title']       = $title;
        if($description) $params['description'] = $description;
        if($tags)        $params['tags']        = $tags;  // Space-separated string
        if($perms) {
            if(isset($perms['is_public'])) $params['is_public'] = $perms['is_public'];
            if(isset($perms['is_friend'])) $params['is_friend'] = $perms['is_friend'];
            if(isset($perms['is_family'])) $params['is_family'] = $perms['is_family'];
        }
        if($async)       $params['async']       = $async;
        print "params = ";
        print_r($params);
        $xml = $this->callMethod('upload',$params);
        print_r($xml);
        if($tmpf) unlink($tmpf);
        if(!$xml) { return FALSE; }

        if($async) return((string)$xml->ticketid);
        else return((string)$xml->photoid);
    }

}
?>