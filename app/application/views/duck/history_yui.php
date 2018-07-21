<table>
		<tr>
			<td>Your Ducks:</td>
			<td>All Ducks:</td></tr>
		<tr>
			<td><?php echo form_dropdown('user_duck_id', $user_duck_list, $duck_id, 'onChange="javascript:formHandler(this)"' ); ?></td>
			<td><?php echo form_dropdown('total_duck_id', $total_duck_list, $duck_id, 'onChange="javascript:formHandler(this)"' ); ?></td></tr>
</table>

<style type="text/css">
        /*margin and padding on body element
          can introduce errors in determining
          element position and are not recommended;
          we turn them off as a foundation for YUI
          CSS treatments. */
        body {
            margin:0;
			padding:0;
        }
</style>


<link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/2.5.2/build/fonts/fonts-min.css" />
<link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/2.5.2/build/datatable/assets/skins/sam/datatable.css" />
<script type="text/javascript" src="http://yui.yahooapis.com/2.5.2/build/yahoo-dom-event/yahoo-dom-event.js"></script>

<script type="text/javascript" src="http://yui.yahooapis.com/2.5.2/build/dragdrop/dragdrop-min.js"></script>
<script type="text/javascript" src="http://yui.yahooapis.com/2.5.2/build/element/element-beta-min.js"></script>
<script type="text/javascript" src="http://yui.yahooapis.com/2.5.2/build/datasource/datasource-beta-min.js"></script>
<script type="text/javascript" src="http://yui.yahooapis.com/2.5.2/build/datatable/datatable-beta-min.js"></script>

<div class=" yui-skin-sam">
<div id="basic"></div> 
        <script type="text/javascript" language="JavaScript">
function formHandler(obj)
{
	var duck_id = obj[obj.selectedIndex].value;
	var URL = '<?php echo $base_url; ?>index.php/history/duck/' + duck_id;
	window.location.href = URL;
}

var history_data = {
	data : <?php echo json_encode($duck_history); ?>
}

YAHOO.util.Event.addListener(window, "load", function() {
    YAHOO.example.Basic = new function() {
        var myColumnDefs = [
            {key:"duck_id", sortable:true, resizeable:true},
            {key:"timestamp", formatter:YAHOO.widget.DataTable.formatDate, sortable:true, sortOptions:{defaultDir:YAHOO.widget.DataTable.CLASS_DESC},resizeable:true},
            {key:"action", formatter:YAHOO.widget.DataTable.formatNumber, sortable:true, resizeable:true},
            {key:"username", formatter:YAHOO.widget.DataTable.formatCurrency, sortable:true, resizeable:true},
            {key:"comment", sortable:true, resizeable:true}
        ];

        this.myDataSource = new YAHOO.util.DataSource(history_data.data);
        this.myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
        this.myDataSource.responseSchema = {
            fields: ["duck_id","username","action","timestamp","comment"]
        };

        this.myDataTable = new YAHOO.widget.DataTable("basic",
                myColumnDefs, this.myDataSource, {caption:"DataTable Caption"});
    };
});


       </script>
</div>

Duckie Assignments:</br>
<table border=1>
<?php  foreach ($duck_history as $duck) { ?>
    <tr>
        <td><?php echo $duck['duck_id'] . " - {$duck['duck_name']}" ?></td>
        <td><?php echo $duck['username'] ?></td>
        <td><?php echo $duck['action'] ?></td>
        <td><?php echo date('r', $duck['timestamp']) ?></td>
        <td><?php echo $duck['comment'] ?></td>
    </tr>
<?php } ?>

</table>

