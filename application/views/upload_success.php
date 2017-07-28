<html>
<head>
<title>Upload Form</title>
</head>
<body>

<h3>Success!</h3>
<ul>
<?php
    foreach ($upload_data as $idx => $file_data) {
        echo "<h3>a file was successfully uploaded!</h3>\n";
        foreach ($file_data as $item => $value) {
            echo "<li>$item: $value</li>\n";
        }
    }
?>
</ul>
<p><?php echo anchor('upload', 'Upload Another File!'); ?></p>

</body>
</html>
