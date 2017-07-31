<?php defined('BASEPATH') OR exit('No direct script access allowed');

class Upload_Flickr extends CI_Controller {

        public function __construct()
        {
                parent::__construct();
                $this->load->helper(array('form', 'url'));
                $this->view_data = array('form_dest' => 'upload_flickr/do_upload', 'error' => ' ' );
        }

        public function index()
        {
                $this->load->view('upload_form', $this->view_data);
        }

        public function do_upload()
        {
                $config['upload_path']          = './uploads/';
                $config['allowed_types']        = 'gif|jpg|png';
                $config['max_size']             = 32 * 1024;
                $duck_id = 'deleteme';
                $desc = 'testupload';

                $this->load->library('upload', $config);

                $upload_data = $this->upload->do_multi_upload("files");

                if ( $upload_data )
                {
                        $flickr_config = array(
                                'consumer_key' => getenv('FLICKR_API_KEY'),
                                'consumer_secret' => getenv('FLICKR_API_SECRET'));
                        $this->load->library('Flickr', $flickr_config);
                        $this->flickr->setOauthData('oauth_access_token', getenv('FLICKR_ACCESS_TOKEN'));
                        $this->flickr->setOauthData('oauth_access_token_secret', getenv('FLICKR_ACCESS_TOKEN_SECRET'));
                        $this->flickr->setOauthData('user_nsid', getenv('FLICKR_USER_NSID'));
                        $this->flickr->setOauthData('user_name', getenv('FLICKR_USER_NAME'));
                        $this->flickr->setOauthData('permissions', getenv('FLICKR_PERMISSIONS'));
                        if (!$this->flickr->authenticate('write')) {
                                $this->view_data['error'] = 'unable to authenticate with Flickr';
                                $this->load->view('upload_form', $this->view_data);
                        }

                        foreach ($upload_data as $idx => $pic) {
                                $title = 'Duck #' . $duck_id;
                                $pic_desc = $desc . "<br/>\n" . anchor("http://duckiehunt.com/view/duck/{$duck_id}");
                                $tags  = "duckiehunt,rubber duckie,duckie,duck{$duck_id}";
                                $is_public =  TRUE;
                                $async = FALSE;
                                $parameters = array(
                                    'title' => $title,
                                    'tags' => $tags,
                                    'description' => $pic_desc,
                                    'photo' => curl_file_create($pic['full_path']),
                                    'is_public' => 0, // TODO:  Remove for prod
                                    'hidden' => 2, // TOOD: Remove for prod
                                );

                                $photo_info = $this->flickr->upload($parameters);
//                                print 'photo_info=';
//                                print_r($photo_info);
                                if (!$photo_info ) {
                                        error_log('Received an error');
                                        $error_code = $this->flickr->error_code;
                                        $error_msg = $this->flickr->error_msg;
                                        $this->view_data['error'] = $error_msg;
                                        $this->load->view('upload_form', $this->view_data);
                                        return;
                                }
                                $photo_id = $photo_info['photoid']['_content'];
                                $upload_data[$idx]['flickr_photo_id'] = $photo_id;

//                                $response = $this->flickr->call('flickr.photos.getInfo', array('photo_id' => $photo_id));
//                                print 'response=';
//                                print_r($response);

                        }
                        $this->view_data['upload_data'] = $upload_data;
                        $this->load->view('upload_success', $this->view_data);
                } else  {
                        $this->view_data['error'] =  $this->upload->display_errors();
                        $this->load->view('upload_form', $this->view_data);
                }
        }
}