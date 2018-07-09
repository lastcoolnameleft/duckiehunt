<form  target="hiddenframe" enctype="multipart/form-data" action="upload/process" method="POST" name="uploadform">
<p>
  <label>To:
  <input name="textfield2" type="text" id="textfield2" size="60" maxlength="60" />
  <br />
  <br />
  Subject:
  <input name="textfield" type="text" id="textfield" size="60" maxlength="60" />
  <br />
  <br />
  Attach File:
  <input type="file" name="filefieldname" id="fileField"   onchange="document.uploadform.submit()"/>
  </label>
</p>
<p id="uploadedfile" >
  <label></label>
</p>
<p>
  <label>
  <input type="submit" name="button" id="button" value="Submit" />
  </label>
</p>
<iframe name="hiddenframe" style="display:none" >Loading...</iframe>
</form>
<p>&nbsp; </p>
