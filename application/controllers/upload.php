<?php 

class Upload extends Controller {
    
    function Upload()
    {
        parent::Controller();
        $this->load->helper(array('form', 'url'));
    }
    
    function index()
    {    
        $this->load->view('upload_form');
    }

    function do_upload()
    {
        $config['upload_path'] = './uploads/'; // server directory
        $config['allowed_types'] = 'gif|jpg|png'; // by extension, will check for whether it is an image
        $config['max_size']    = '1000'; // in kb
        $config['max_width']  = '1024';
        $config['max_height']  = '768';
        
        $this->load->library('upload', $config);
        $this->load->library('Multi_upload');
    
        $files = $this->multi_upload->go_upload();
        
        if ( ! $files )        
        {
            $error = array('error' => $this->upload->display_errors());
            $this->load->view('upload_form', $error);
        }    
        else
        {
            $data = array('upload_data' => $files);
            $this->load->view('upload_success', $data);

            $this->load->library('Flickr_API');
//            require_once('system/application/libraries/Flickr_API.php');
            $data = array('upload_data' => $files);
            $token = getenv('FLICKR_TOKEN');
            $secrets = array(
                'api_key'=> getenv('FLICKR_API_KEY'),
                'api_secret' => getenv('FLICKR_API_SECRET'));
            $flickr = new Flickr($secrets);
            $flickr->token = $token;
//            print_r($data);
            foreach ($data['upload_data'] as $pic) {
//                print_r($pic);
                $duck_id = $this->input->post('duck_id');
                $title = 'Duck #' . $duck_id;
                $desc = anchor("http://duckiehunt.com/view/duck/{$duck_id}");
                $tags = "duckiehunt,rubber duckie, duckie";
                $perms = array("is_public"=>1);
                $async = FALSE;
                
                $photo_id = $flickr->upload($pic['file'], $title, $desc, $tags, $perms, $async);
//                print_r($photo_id);
                $photo = $flickr->photosGetInfo($photo_id);
//                print_r($photo);
                $result[] = $photo['urls']['photopage'];
//                if(!$photo) { $flickr->showError(); exit; }
//                $url = $flickr->getPhotoURL($photo);
//                echo "url = $url";
            }
        }

        return $result;
    }

}
?>
