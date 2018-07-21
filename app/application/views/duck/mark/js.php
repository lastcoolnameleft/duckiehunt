<script type="text/javascript" src="http://api.maps.yahoo.com/ajaxymap?v=3.8&appid=<?php echo $this->config->item('y_app_id') ?>"></script>
<script src="http://yui.yahooapis.com/2.6.0/build/yahoo/yahoo-min.js"></script>
<script src="http://yui.yahooapis.com/2.6.0/build/json/json-min.js"></script>
<script type="text/javascript">


var fields = 0;
function addInput( div, name, count, type, size) {
    if ( document.getElementById(count).value < 9) {
        document.getElementById(count).value = Number(document.getElementById(count).value) + 1;
        var d = document.createElement("div");
        var link = document.createElement("input");
        link.setAttribute("type", type);
        link.setAttribute('size', size);
        link.setAttribute("name", name + document.getElementById(count).value);
        d.appendChild(link);
        document.getElementById(div).appendChild(d);
    }
//document.getElementById(div).innerHTML += "<input size=30 type='text' value='' id='" + name + document.getElementById(count).value + "'/><br />";
}

// Create a Map that will be placed in the "map" div.
var map = new YMap(document.getElementById('map'));
window.onload = startMap;


var xmlhttp;


function centerOnInput( center ) {
	map.drawZoomAndCenter( center );
	GetXYAjaxObject.startRequest( center );
}


function validateData() {
	if ( ! document.form.lat.value || !document.form.lon.value ) {
		alert('You must click on the map to set the duck location!');
		return false;
	}
    return true;
}

// Create a Map that will be placed in the "map" div.
function startMap(){
	if (window.XMLHttpRequest) {
		xmlhttp = new XMLHttpRequest();
		xmlhttp.overrideMimeType('text/xml');
	} else if (window.ActiveXObject) {
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}

	// Add the ability to change between Sat, Hybrid, and Regular Maps
	map.addTypeControl();
	// Add the zoom control. Long specifies a Slider versus a "+" and "-" zoom control
	map.addZoomLong();
	// Add the Pan control to have North, South, East and West directional control
	map.addPanControl();
	// Specifying the Map starting location and zoom level

	var startPoint = new YGeoPoint(37.92686760148135, -94.921875);
	map.drawZoomAndCenter(startPoint,15);

	// Add an event to report to our Logger
	YEvent.Capture(map, EventsList.MouseClick, reportPosition);
}

	function reportPosition(_e, _c){
		addDuckMarker( _c.Lat, _c.Lon );
	}

	function addDuckMarker( lat, lon ) {
			document.form.lat.value = lat;
			document.form.lon.value = lon;

			map.removeMarker('lastMarker');

			// It is optional to specify the location of the Logger.
			// Do so by sending a YCoordPoint to the initPos function.
			var mapCoordCenter = map.convertLatLonXY(map.getCenterLatLon());

			var currentGeoPoint = new YGeoPoint( lat, lon );
			var newMarker= new YMarker(currentGeoPoint, null, 'lastMarker');
//			var new_image = new YImage();
//			new_image.src = '/duck-16x16.png'
//            newMarker.changeImage(new_image);

			map.addOverlay(newMarker);
			newMarker.openAutoExpand()
	}


/*
 * GetXYAjaxObject is a hypothetical object that encapsulates the transaction
 *     request and callback logic.
 *
 * handleSuccess( ) provides success case logic
 * handleFailure( ) provides failure case logic
 * processResult( ) displays the results of the response from both the
 * success and failure handlers
 * call( ) calling this member starts the transaction request.
 */

var GetXYAjaxObject = {

	handleSuccess:function(o){
		// This member handles the success response
		// and passes the response object o to GetXYAjaxObject's
		// processResult member.
		this.processResult(o);
	},

	handleFailure:function(o){
		// Failure handler
	},

	processResult:function(o){
		// This member is called by handleSuccess
		var loc = YAHOO.lang.JSON.parse(o.responseText);
		addDuckMarker( loc.Latitude, loc.Longitude );
	},

	startRequest:function( loc ) {
	   YAHOO.util.Connect.asyncRequest('POST', '/getlatlon', callback, "loc=" + loc);
	}

};

/*
 * Define the callback object for success and failure
 * handlers as well as object scope.
 */
var callback =
{
	success:GetXYAjaxObject.handleSuccess,
	failure:GetXYAjaxObject.handleFailure,
	scope: GetXYAjaxObject
};

    function callWS(target) {
      if(target !== ""){
        var url = encodeURI(target);
        xmlhttp.open('GET', url, true);
        xmlhttp.onreadystatechange = function() {
          if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            document.getElementById('result').innerHTML = '';
            parseResult(xmlhttp.responseText);
          } else {
            document.getElementById('result').innerHTML = "Loading...";
          }
        };
        xmlhttp.send(null);
      }
    }

    function parseResult(parseMeString) {
      var parser = new DOMImplementation();
      var domDoc = parser.loadXML(parseMeString);

      if (domDoc == null)
      {
        alert("There was a problem parsing search results.");
        return;
      }

      var docRoot = domDoc.getDocumentElement();

      var items = docRoot.getElementsByTagName("Result");
        for (var i =0; i < items.length; i++) {
          lat = items.item(i).getElementsByTagName("Latitude").item(0).getFirstChild().getNodeValue();
          lon = items.item(i).getElementsByTagName("Longitude").item(0).getFirstChild().getNodeValue();
          smart = "Long: " + lon +  "<br />" + "Lat: " + lat;
          document.getElementById('result').innerHTML = smart;
        }


    }

    function onLoad() {
      if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
        xmlhttp.overrideMimeType('text/xml');
      } else if (window.ActiveXObject) {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
      }
    }


    function callGeocode() {
      var query = document.getElementById("center").value;
      var uri = "http://api.local.yahoo.com/MapsService/V1/geocode?appid=<?php echo $this->config->item('y_app_id'); ?>&location=" + query;
      callWS(uri);
    }


    function centerOnInputIfValid( center ) {
        if ( center ) {
            centerOnInput(center);
        }
    }

onload(centerOnInputIfValid(document.getElementById("center").value));

</script>