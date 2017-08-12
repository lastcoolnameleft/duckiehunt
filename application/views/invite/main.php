<br/>
<?php

    $this->load->helper('form');
    echo form_open('invite/submit', array('id' => 'form', 'name' => 'form'));
	echo "Invite " .  form_input('email') . " to duckiehunt.com. ";

	echo form_submit('mysubmit', 'go'); 
	echo form_close(); 

?>
