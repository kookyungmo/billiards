// Foundation JS
// Foundation JS
;(function ($, window, undefined) {
  'use strict';

  var $doc = $(document),
      Modernizr = window.Modernizr;
  
  // Include the Foundation JS plugins
  $(document).ready(function() {
    $.fn.foundationAlerts           ? $doc.foundationAlerts() : null;
    $.fn.foundationButtons          ? $doc.foundationButtons() : null;
    $.fn.foundationAccordion        ? $doc.foundationAccordion() : null;
    $.fn.foundationNavigation       ? $doc.foundationNavigation() : null;
    $.fn.foundationTopBar           ? $doc.foundationTopBar() : null;
    $.fn.foundationCustomForms      ? $doc.foundationCustomForms() : null;
    $.fn.foundationMediaQueryViewer ? $doc.foundationMediaQueryViewer() : null;
    $.fn.foundationTabs             ? $doc.foundationTabs({callback : $.foundation.customForms.appendCustomMarkup}) : null;
    $.fn.foundationTooltips         ? $doc.foundationTooltips() : null;
    //$.fn.foundationMagellan         ? $doc.foundationMagellan() : null;
    //$.fn.foundationClearing         ? $doc.foundationClearing() : null;

    $.fn.placeholder                ? $('input, textarea').placeholder() : null;
  });

  // UNCOMMENT THE LINE YOU WANT BELOW IF YOU WANT IE8 SUPPORT AND ARE USING .block-grids
  // $('.block-grid.two-up>li:nth-child(2n+1)').css({clear: 'both'});
  // $('.block-grid.three-up>li:nth-child(3n+1)').css({clear: 'both'});
  // $('.block-grid.four-up>li:nth-child(4n+1)').css({clear: 'both'});
  // $('.block-grid.five-up>li:nth-child(5n+1)').css({clear: 'both'});

  // Hide address bar on mobile devices (except if #hash present, so we don't mess up deep linking).
  if (Modernizr.touch && !window.location.hash) {
    $(window).load(function () {
      setTimeout(function () {
        window.scrollTo(0, 1);
      }, 0);
    });
  }
  
})(jQuery, this);

/* ----------------------------------------------*/	
// Ridiculous Lazy Load "RLL" the images when the page is displayed
// Use window load not document ready so it fires after page load & display
$(window).load(function(){
	// For each image with the datatype src do the following
	$('img[data-src]').each(function() {
		// Replace the src value with the datatype value
		$(this).attr('src', $(this).attr('data-src'));
		// Alert the values
		//alert($(this).attr('data-src'));
	});
});
/* ----------------------------------------------*/	


$(document).ready(function () {
	/* ----------------------------------------------*/
	// Path sidebar styling
	// For each of the required steps
	$('a.requirement').each(function (index) {
	   // If the anchor is the same as the page make it the active path item
	   if(window.location.pathname == $(this).attr('href')) { 
	    // Mark it as checked (Display only)
	   	$(this).delay(3000).addClass('checked');
	   	// Show the path container where this article is contained
	   	$(this).closest('div#profile-path-container').show();
	   	// Remove the empty checkbox and replace it with the eye icon
	   	$(this).children('i').removeClass('icon-check-empty').removeClass('icon-check').addClass('icon-eye-open');
	   	}
	 });
	/* ----------------------------------------------*/
	// Trigger input drop down anchor select
	$('.nsSelect select').each(function (index) {
	    $(this).prev('a').html($(this).children(':selected').text());
	    $(this).fadeTo(0);
	});
	$('.nsSelect select').focusin(function() {
		$(this).trigger('click');
	});
	$('.nsSelect select').change(function (event) {
	    $(this).prev('a').html($(this).children(':selected').text());
	});
	$('.nsSelect a').click(function () {
	    return false;
	});
	/* ----------------------------------------------*/	
	
	
 
	/* ----------------------------------------------*/
	// Sidebar div height for float and scroll
	// Assign a variable for the application being used
	var nVer = navigator.appVersion;
	// Assign a variable for the device being used
	var nAgt = navigator.userAgent;
	var nameOffset,verOffset,ix;
	
	// First check to see if the platform is an iPhone or iPod
	if(navigator.platform == 'iPhone' || navigator.platform == 'iPod'){
		// In Safari, the true version is after "Safari" 
		if ((verOffset=nAgt.indexOf('Safari'))!=-1) {
		  // Set a variable to use later
		  var mobileSafari = 'Safari';
		}
	}
	
	// If is mobile Safari set window height +60
	if (mobileSafari == 'Safari') { 
		// Height + 60px
		$('#right-sidebar').css('height',(($(window).height()) + 60)+'px');
		$('#left-content').css('min-height',(($(window).height()) + 60)+'px');
	} else {
		// Else use the default window height
		$('#right-sidebar').css('height',(($(window).height()))+'px');
		$('#left-content').css('min-height',(($(window).height()))+'px');
	};
	
	// This is not DRY. I need to make it a function! :P
	// On device rotate reset the height
	$(window).bind( 'orientationchange', function(e){
		// If is mobile Safari set window height +60
			if (mobileSafari == 'Safari') { 
				// Height + 60px
				$('#right-sidebar').css('height',(($(window).height()) + 60)+'px');
				$('#left-content').css('min-height',(($(window).height()) + 60)+'px');
		//		alert($(window).height());
				
			} else {
				// Else use the default window height
				$('#right-sidebar').css('height',(($(window).height()))+'px');
				$('#left-content').css('min-height',(($(window).height()))+'px');
			};
	});
	
	// On window resize reset the heights.
	$(window).resize(function() {
	  $('#right-sidebar').css('height',(($(window).height()))+'px');
	  //$('#left-content').css('min-height',(($(window).height()))+'px');
	});
	/* ----------------------------------------------*/	
	
	
	
	/* ----------------------------------------------*/	
	// Add to Homescreen
	// If is window mode do the following
	if (window.navigator.standalone) {
		$('body').addClass('standalone');
	    // Slide open if opened via web app
//		setTimeout(function() {
//			$('#ns-tool-bar, #left-content, #right-sidebar, #slide-close, #search-bar, .list-navigation').toggleClass('slide');
//		}, 1000);
	
		// Ajax load page content for urls.
		$('a').live('click', function(){
			// get the url of the href and locate the left content.
			var url = this.href+' #left-content > *';
			// Then fade out left content
		    $('#left-content').fadeTo('normal', 0.0, function() {
		    	// Load the new left content and fade back in.
		    	$('#left-content').load(url, function() {
		    		$('#left-content').fadeTo('slow', 1.0);
		    	});
		    });
			
		    return false;
		});
	
	}
	/* ----------------------------------------------*/	
	
	
	
	/* ----------------------------------------------*/	
	// Parsley form validation
	$('#Form').attr('data-validate','parsley');
	// On the input change
	$('.CustomParsleySelect').change(function() {
		
		// Removes the duplicate error list
		$(this).parent().siblings('ul.parsley-error-list').remove();
		
		// Get the value of the changed select
		var selectVal = $(this).val();
		
		if (selectVal == '') {
			// If the value is 0 then make it error out
			$(this).parent().removeClass('parsley-success');	
			$(this).parent().addClass('parsley-error');
			$('#not-good-to-go').show();
			// Move the error ul up a level
			var errorMessage = $(this).siblings('ul').clone();
			$(this).parent().parent().append(errorMessage);
		} else {
			// If this value is not 0 then it's a success
			$(this).parent().removeClass('parsley-error');
			$(this).parent().addClass('parsley-success');
			$('#not-good-to-go').hide();
		}
	});
	
	/* ----------------------------------------------*/
	// Fix the DNN Foundation conflict issues with styling and menus
	setTimeout(function() {
	    $('.jspPane').removeClass('jspPane');
	    $('.rcbScroll').removeClass('rcbScroll');
	    $('.jspContainer').removeClass('jspContainer');
	    $('.jspScrollable').removeClass('jspScrollable');
	    $('.RadComboBoxDropDown').removeClass('RadComboBoxDropDown');
	    $('.RadComboBoxDropDown_Default').removeClass('RadComboBoxDropDown_Default');
	    $('.rcbSlide').removeClass('rcbSlide');	
	}, 100);
	/* ----------------------------------------------*/	
	
});
// End the document ready script

/* ----------------------------------------------*/	
// Custom error tracking
$.fn.errorTracking = function() { 
	// Save the errors to analytics
	$('.parsley-li-error').each(function() {
		// Get the error type
		var errorType = $(this).attr('class');
		var errorType = errorType.replace('parsley-li-error ', '');
		// Get the error Text
		var errorText = $(this).text();
		// Get the label from where the error is
		var errorParent = $(this).parents().siblings('label').text();
		// Combine them into one string
		var errorDescription = errorParent + ' ' + errorText + ' - ' + errorType;
		// Record all click errors as a click event
		_gaq.push(['_trackEvent', 'Error', 'click', errorDescription]);
		//$(this).text(errorDescription);
		
		// Temp to track state error
	    //var errorValue = $(this).parents().siblings('select, input').val();
		var errorValue = $(this).parents().prev().val();
		var currentPage = window.location.pathname;
		var browserVersion = $.browser.version;
		errorDescriptionURL = errorParent + ' : ' + errorValue + ' : ' + currentPage + ' : ' + browserVersion;
		_gaq.push(['_trackEvent', 'Error-Page', 'click', errorDescriptionURL]);
	});
	// Count the amount of errors that were on submit
	var errorCount = 'Errors-' + $('.parsley-error').length;
	// Post the Errors Per event tracking
	_gaq.push(['_trackEvent', 'Errors-Per', 'click', errorCount]);	
	// Adds the inactive class allowing time for errors to be fixed
	$('.regNextButton').addClass('inactive');
	// After pause allow for click again.
	setTimeout(function() {
	     $('.regNextButton').removeClass('inactive');
	}, 3000);
}
/* ---------------------------------------------- */	

/* ---------------------------------------------- */
// Trag user visit prior to leaving the site
$(document).ready(function(){
  var element_to_track = '#left-content'; //set this to whatever element you want to track. this is the only thing you need to change.
  var scroll_reach = 0;
  var temp_scroll_reach = 0;
  var scroll_reach_pixels = 0;
  var temp_scroll_reach_pixels = 0;
  $(window).scroll(function(){
    temp_scroll_reach = Math.floor(100 * ($(window).scrollTop() + $(window).height() - $(element_to_track).position().top) / $(element_to_track).height());
    temp_scroll_reach_pixels = Math.floor($(window).scrollTop() + $(window).height());
    if(temp_scroll_reach > scroll_reach){
      scroll_reach = temp_scroll_reach;
      scroll_reach_pixels = temp_scroll_reach_pixels;
    }
  });
  $(window).on('beforeunload', function() {
    _gaq.push(['_trackEvent', 'Scroll Depth', 'Percentage', '', scroll_reach]);
    _gaq.push(['_trackEvent', 'Scroll Depth', 'Pixels', '', scroll_reach_pixels]);
  });
});
/* ---------------------------------------------- */