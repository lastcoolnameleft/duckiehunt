<?php
 echo "<center><h2>{$user_info['username']}</h2></center>\n";
?>
<div id='page'>
    <div class="width25 floatLeft leftColumn gradient">
        <ol>
<?php foreach ($location_list as $location) { ?>
            <li><?php echo anchor("/view/location/{$location['duck_location_id']}",  $location['location'] . " ({$location['distance_to']} mi)" ) ?></li>
<?php } ?>
        </ol>
    </div>

    <div class="width75 floatRight gradient">
        <center>
            <b>Total Distance = <?php echo $total_distance ?> Miles<br /></b>
            <div id="map"></div>
       </center>
    </div>
</div>
