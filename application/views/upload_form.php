<html>
<head>
<title>Upload Form</title>
</head>
<body>

<?php echo $error;?>

<?php echo form_open_multipart($form_dest);?>

<input type="file" name="files[]" size="20" multiple />

<br /><br />

<input type="submit" value="upload" />

</form>

</body>
</html>
