<h2>You've found an unnamed duck!</h2>
Since this duck is not yet named, you can submit one.  Please be creative, not dirty.<br/>
<input type='hidden' id='duck_id' value='<?php echo $duck_id ?>' >
<div id="result_msg"></div>
<input type='text' id='duck_name' size='30' maxlength="30">
<input type="button" id="name_btn" value="Submit">

<script src="/js/yui-2.6.0.js"></script>
<script type='text/javascript'>
    // http://yui.yahooapis.com/combo?2.6.0/build/yahoo/yahoo-min.js&2.6.0/build/event/event-min.js&2.6.0/build/connection/connection-min.js&2.6.0/build/dom/dom-min.js&2.6.0/build/json/json-min.js

    YAHOO.util.Event.on('name_btn','click',function (e) {
        // Get the div element in which to report messages from the server
        var msg_section = YAHOO.util.Dom.get('result_msg');
        msg_section.innerHTML = '';


        var callbacks = {
            // Successful XHR response handler
            success : function (o) {
                var messages = [];

                // Use the JSON Utility to parse the data returned from the server
                try {
                    result = YAHOO.lang.JSON.parse(o.responseText);
                }
                catch (x) {
                    alert("JSON Parse failed!");
                    return;
                }

                var p = document.createElement('p');
                var message_text = document.createTextNode( result.message );
                p.appendChild(message_text);
                msg_section.appendChild(p);
            },

            failure : function (o) {
                if (!YAHOO.util.Connect.isCallInProgress(o)) {
                    alert("Name Set Failed!");
                }
            },

            timeout : 3000
        }


        var duck_id = YAHOO.util.Dom.get('duck_id').value;
        var duck_name = YAHOO.util.Dom.get('duck_name').value;
        // Make the call to the server for JSON data
        YAHOO.util.Connect.asyncRequest('POST',"/mark/setname/" + duck_id, callbacks, 'name=' + duck_name);
    });

</script>
<br/>
<br/>