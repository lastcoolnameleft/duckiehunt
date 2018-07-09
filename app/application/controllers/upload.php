<?php

class Upload extends CI_Controller {

        public function __construct()
        {
                parent::__construct();
                $this->load->helper(array('form', 'url'));
        }

        public function index()
        {
                $this->load->view('upload_form', array('form_dest' => 'upload/do_upload', 'error' => ' ' ));
        }

        public function do_upload()
        {
                $config['upload_path']          = './uploads/';
                $config['allowed_types']        = 'gif|jpg|png';

                $this->load->library('upload', $config);

                $upload_data = $this->upload->do_multi_upload("files");

                if ( $upload_data )
                {
                        $data = array('upload_data' => $upload_data, 'form_dest' => 'upload/do_upload');
                        $this->load->view('upload_success', $data);
                } else  {
                        $error = array('error' => $this->upload->display_errors(), 'form_dest' => 'upload/do_upload');
                        $this->load->view('upload_form', $error);
                }
        }
}
?>
