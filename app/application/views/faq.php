    <!-- Page Content -->
    <div class="container">

      <!-- Page Heading/Breadcrumbs -->
      <h1 class="mt-4 mb-3">FAQ
      </h1>

      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <a href="/">Home</a>
        </li>
        <li class="breadcrumb-item active">FAQ</li>
      </ol>

      <div class="mb-4" id="accordion" role="tablist" aria-multiselectable="true">
        <div class="card">
          <div class="card-header" role="tab" id="headingTwo">
            <h5 class="mb-0">
              <a class="collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">Why do you have so many duckies?
              </a>
            </h5>
          </div>
          <div id="collapseTwo" class="collapse show" role="tabpanel" aria-labelledby="headingTwo">
            <div class="card-body">
				<p>The genesis of this was from "The Duckening".</p>
				<p>My lovely wife and I were away on our honeymoon and our friends conspired towards a <?php echo anchor('http://flickr.com/photos/nmlittle/tags/duckieinvation/', 'huge rubber duckie invasion') ?>.  We came back to <?php echo anchor('http://flickr.com/photos/snoopykiss/sets/72157607146654923/', '1000+ duckies in the house') ?>.  <?php echo anchor('http://flickr.com/photos/snoopykiss/2833050713', '~300 on the bed') ?>.  Days later I went into work to find <?php echo anchor('http://flickr.com/photos/snoopykiss/2833067647', '~200 more there') ?>.  It was epic.</p>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header" role="tab" id="headingOne">
            <h5 class="mb-0">
              <a data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="true" aria-controls="collapseOne">Why are you doing this?</a>
            </h5>
          </div>

          <div id="collapseOne" class="collapse" role="tabpanel" aria-labelledby="headingOne">
            <div class="card-body">
              Because.
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header" role="tab" id="headingThree">
            <h5 class="mb-0">
              <a class="collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapseThree" aria-expanded="false" aria-controls="collapseThree">Who gave you all of these ducks?</a>
            </h5>
          </div>
          <div id="collapseThree" class="collapse" role="tabpanel" aria-labelledby="headingThree">
            <div class="card-body">
				Not everyone has fessed up to <i>The Great Duckie Invasion of 2008</i>&trade;, but so far the list of suspects is:
				<ul>
				<li><?php echo anchor('http://burningnerd.com', 'Neil Little') ?></li>
				<li>Lee Gibson</li>
				<li><?php echo anchor('http://robertames.com', 'Robert Ames') ?></li>
				<li>Abel Rios</li>
				</ul>
   		    </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header" role="tab" id="headingFour">
            <h5 class="mb-0">
              <a class="collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapseFour" aria-expanded="false" aria-controls="collapseFour">Who built this website?</a>
            </h5>
          </div>
          <div id="collapseFour" class="collapse" role="tabpanel" aria-labelledby="headingFour">
            <div class="card-body">
				<p>Me.</p>
				<p>I used to be a developer for Yahoo!, but now I'm a Cloud Solution Architect at Microsoft. This is my lifeblood.</p>
				<p>It's currently running on an AKS cluster in Microsoft Azure.
				I even <a href='https://www.lastcoolnameleft.com/2018/07/the-journey-to-kubernetes/'>blogged about the technical aspects</a>.</p>
   		    </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header" role="tab" id="headingFive">
            <h5 class="mb-0">
              <a class="collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapseFive" aria-expanded="false" aria-controls="collapseFive">What's your Privacy Policy?</a>
            </h5>
          </div>
          <div id="collapseFive" class="collapse" role="tabpanel" aria-labelledby="headingFive">
            <div class="card-body">
			  You can see our privacy policy <a href='/privacy'>here</a>
   		    </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header" role="tab" id="headingSix">
            <h5 class="mb-0">
              <a class="collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapseSix" aria-expanded="false" aria-controls="collapseSix">What's your Terms of Service?</a>
            </h5>
          </div>
          <div id="collapseSix" class="collapse" role="tabpanel" aria-labelledby="headingSix">
            <div class="card-body">
			  You can see our Terms of Service <a href='/tos'>here</a>
   		    </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header" role="tab" id="headingSeven">
            <h5 class="mb-0">
              <a class="collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapseSeven" aria-expanded="false" aria-controls="collapseSeven">How do I contact you?</a>
            </h5>
          </div>
          <div id="collapseSeven" class="collapse" role="tabpanel" aria-labelledby="headingSeven">
            <div class="card-body">
			  <?php echo mailto('tommy@duckiehunt.com') ?>
   		    </div>
          </div>
        </div>
      </div>

    </div>
    <!-- /.container -->
