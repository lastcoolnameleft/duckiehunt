<?php

class Upload extends CI_Controller {

        public function __construct()
        {
                parent::__construct();
                $this->load->helper(array('form', 'url'));
        }

        public function index()
        {
                $this->load->view('upload_form', array('error' => ' ' ));
        }

        public function do_upload()
        {
                $config['upload_path']          = './uploads/';
                $config['allowed_types']        = 'gif|jpg|png';
                $config['max_size']             = 32 * 1024;

                $this->load->library('upload', $config);

                $upload_data = $this->upload->do_multi_upload("files");

                if ( $upload_data )
                {
                        $data = array('upload_data' => $upload_data);
                        $this->load->view('upload_success', $data);
                } else  {
                        $error = array('error' => $this->upload->display_errors());
                        $this->load->view('upload_form', $error);
                }
        }
}
?>
