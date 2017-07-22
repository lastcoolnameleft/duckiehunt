<br/>
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
		.yui-dt-liner {
			color:#000000;
		}
		.yui-dt-col-duck_id a:link {
			color:black;
		}
		.yui-dt-col-duck_id a:hover {
			color:red;
		}
		.yui-dt-col-username a:link {
			color:black;
		}
		.yui-dt-col-username a:hover {
			color:red;
		}
</style>



<!-- Combo-handled YUI CSS files: -->
<link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/combo?2.7.0/build/datatable/assets/skins/sam/datatable.css">
<!-- Combo-handled YUI JS files: -->
<script type="text/javascript" src="http://yui.yahooapis.com/combo?2.7.0/build/yahoo-dom-event/yahoo-dom-event.js&2.7.0/build/element/element-min.js&2.7.0/build/datasource/datasource-min.js&2.7.0/build/datatable/datatable-min.js"></script>




<div class="yui-skin-sam">
<table>
    <tr>
        <td><h2>Most Miles - Duck</h2></td>
        <td><h2>Most Miles - User</h2></td>
    </tr>
    <tr>
        <td valign='top'><div id="ducks"></div></td>
        <td valign='top'><div id="users"></div></td>
    </tr>
</table>

</div>

<script type="text/javascript" language="JavaScript">
var duck_data = {
	data : <?php echo json_encode($ducks); ?>
}

var user_data = {
	data : <?php echo json_encode($users); ?>
}


// Override the built-in formatter 
YAHOO.widget.DataTable.formatDuck = function(elCell, oRecord, oColumn, oData) { 
    var duck_id = oData;
    elCell.innerHTML = "<a href='/view/duck/" + duck_id + "'>" + duck_id+ "</a>"; 
};

YAHOO.widget.DataTable.formatUser = function(elCell, oRecord, oColumn, oData) {
    var username = oData;
    elCell.innerHTML = "<a href='/user/" + username + "'>" + username + "</a>";
};

YAHOO.util.Event.addListener(window, "load", function() {
    YAHOO.example.Basic = new function() {
        //  Do the Ducks
        var duckColumnDefs = [
            {key:"duck_id", sortable:true, resizeable:true, label:"Duck", sortable:false, formatter:YAHOO.widget.DataTable.formatDuck},
            {key:"name", sortable:true, resizeable:true, label:"Name", sortable:false},
            {key:"total_distance", sortable:true, resizeable:true, label:"Distance (mi)", sortable:false}
        ];

        this.duckDataSource = new YAHOO.util.DataSource(duck_data.data);
        this.duckDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
        this.duckDataSource.responseSchema = {
            fields: ["duck_id", "name", "total_distance"]
//            fields: ["duck_id","username","action","timestamp","comment"]
        };
        this.myDataTable = new YAHOO.widget.DataTable("ducks", duckColumnDefs, this.duckDataSource);


        //  Do the users
        var userColumnDefs = [
            {key:"username", sortable:true, resizeable:true, label:"User", sortable:false, formatter:YAHOO.widget.DataTable.formatUser},
//            {key:"name", sortable:true, resizeable:true, label:"Name", sortable:false},
            {key:"total_distance", sortable:true, resizeable:true, label:"Distance (mi)", sortable:false}
        ];

        this.userDataSource = new YAHOO.util.DataSource(user_data.data);
        this.userDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
        this.userDataSource.responseSchema = {
            fields: ["username", "total_distance"]
        };

        this.myDataTable = new YAHOO.widget.DataTable("users", userColumnDefs, this.userDataSource);

    };
});

</script>

