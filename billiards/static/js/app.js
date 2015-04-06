function setGetParameter(url, paramName, paramValue)
{
	paramValue = encodeURIComponent(paramValue);
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName));
        var suffix = url.substring(url.indexOf(paramName)).substring(url.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
    if (url.indexOf("?") < 0)
        url += "?" + paramName + "=" + paramValue;
    else
        url += "&" + paramName + "=" + paramValue;
    }
    return url;
}

function dologin(url) {
	dologin2(url, window.location.pathname + window.location.search);
}

function dologin2(url, returnurl) {
	window.location.href = setGetParameter(url, 'returnurl', returnurl);
}

function safeLogoutSOHOCS() {
	var img = new Image(); 
	img.src='http://changyan.sohu.com/api/2/logout?client_id=cyrxYk4s5';
}

function doLogout(url) {
	safeLogoutSOHOCS();
	window.location.href = url;
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function jsonescape(str) {
	return str
    .replace(/[\\]/g, '\\\\')
    .replace(/[\/]/g, '\\/')
    .replace(/[\b]/g, '\\b')
    .replace(/[\f]/g, '\\f')
    .replace(/[\n]/g, '\\n')
    .replace(/[\r]/g, '\\r')
    .replace(/[\t]/g, '\\t');
}

function getFormattedTime(timestr) {
	return moment(timestr).lang('zh_CN').format('MMM Do')
}

function getFormattedTime2(timestr) {
	return moment(timestr).lang('zh_CN').format('h:mm a')
}

function getFormattedTimeToWeekDay(timestr) {
	return moment(timestr).lang('zh_CN').format('dddd')
}

function getFormattedTimeToDate(timestr) {
	if (moment(timestr).year() == moment().year())
		return moment(timestr).lang('zh_CN').format('MMM Do dddd, h:mm a' )
    else
    	return moment(timestr).lang('zh_CN').format('YYYY MMM Do dddd, h:mm a' )
}

function getSmartTime(datetime) {
	if (moment(datetime).format("MM-DD-YYYY") == moment().format("MM-DD-YYYY")) {
		return "今天 " + getFormattedTime2(datetime);
	}
	return getFormattedTimeToDate(datetime);
}

abideOptions = {
		patterns : {
			cellphone: /^1\d{10}$/,
			qq: /^\d{5,13}$/,
		},
		validators: {
			greaterThan: function(el, required, parent) {
				var from  = moment(document.getElementById(el.getAttribute(this.add_namespace('data-greaterThan'))).value, "hh:mm A"),
				to    = moment(el.value, "hh:mm A"),
				valid = (from < to);
				return valid;
			}
		}
};

function isSmall() {
    return matchMedia(Foundation.media_queries.small).matches &&
      !matchMedia(Foundation.media_queries.medium).matches;
}

function isWechat() {
	var ua = navigator.userAgent.toLowerCase();
    if(ua.match(/MicroMessenger/i)=="micromessenger") {
        return true;
    } else {
        return false;
    }
}

function openMap(name, objType, objId) {
	$("#mapModal #title").text(name);
	var originalSrc = PKMAP_URL;
	var newurl = setGetParameter(originalSrc, "type", objType);
	newurl = setGetParameter(newurl, "id", objId);
	$("#mapModal iframe").attr("src", newurl);
	$('#mapModal').foundation('reveal', 'open');
}

function initialMomentTZ() {
	moment.tz.add({
	    "zones": {
	        "Asia/Chongqing": [
	            "7:6:20 - LMT 1928 7:6:20",
	            "7 - LONT 1980_4 7",
	            "8 PRC C%sT"
	        ]
	    },
	    "rules": {
	        "PRC": [
	            "1986 1986 4 4 7 0 0 1 D",
	            "1986 1991 8 11 0 0 0 0 S",
	            "1987 1991 3 10 0 0 0 1 D"
	        ]
	    },
	    "links": {}
	});
}

function loginFirst() {
	$('#quickLogin').foundation('reveal', 'open');
}

function completeInfo() {
	$('#userInfoForm').foundation('reveal', 'open');
}

function applyChallenge(objdiv, id) {
	url = CHALLENGE_APPLY_URL;
	$.ajax({
		url : url.replace(/000/g, id),
		dataType : 'json',
		success : function(data)
		{
			objdiv.children("#enroll").text('应战已提交到俱乐部');
			objdiv.children("#enroll").addClass('disabled');
		},
		error: function (xhr, ajaxOptions, thrownError) {
			if (xhr.status == 403) {
				loginFirst();
		    }
	     }
	});
}

function inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

var UUID_PATTERN = new RegExp("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "g");

function wechatLogin() {
	if (isWechat()){
		$('#wechatlogin').removeClass('hide');
	}
}

(function initialize(){
	  $.ajaxSetup({ 
		     beforeSend: function(xhr, settings) {
		         function getCookie(name) {
		             var cookieValue = null;
		             if (document.cookie && document.cookie != '') {
		                 var cookies = document.cookie.split(';');
		                 for (var i = 0; i < cookies.length; i++) {
		                     var cookie = jQuery.trim(cookies[i]);
		                     // Does this cookie string begin with the name we want?
		                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
		                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		                     break;
		                 }
		             }
		         }
		         return cookieValue;
		         }
		         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
		             // Only send the token to relative URLs i.e. locally.
		             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
		         }
		     } 
		});
	  	$("#doitlater").click(function(){
	  		$("#userInfoForm .close-reveal-modal").click();
	  	});
	  	$("#completeInfoForm").submit(function (e) {
	  		e.preventDefault();
	  		phone = $("#phone").val();
	  		email = $("#email-label").val();
	  		$.ajax({
				data : {'tel': phone, 'email': email},
	  			url : "{% url 'completeInfo' %}",
				dataType : 'json',
				success : function(data) {
					$("#userInfoForm .close-reveal-modal").click();
					location.reload(true);
				},
				error : function() {
					//TODO alert error
				}
			});
	    });
	    $(document).foundation({
	    	abide: abideOptions,
	    });
	    $(document).on('open.fndtn.offcanvas', '[data-offcanvas]', function() {
	    	wechatLogin();
	    });
	    $(function () {
	        $.scrollUp({
	            scrollName: 'scrollUp',      // Element ID
	            scrollDistance: 300,         // Distance from top/bottom before showing element (px)
	            scrollFrom: 'top',           // 'top' or 'bottom'
	            scrollSpeed: 300,            // Speed back to top (ms)
	            easingType: 'linear',        // Scroll to top easing (see http://easings.net/)
	            animation: 'fade',           // Fade, slide, none
	            animationSpeed: 200,         // Animation speed (ms)
	            scrollTrigger: false,        // Set a custom triggering element. Can be an HTML string or jQuery object
	            scrollTarget: false,         // Set a custom target element for scrolling to. Can be element or number
	            scrollText: '', // Text for element, can contain HTML
	            scrollTitle: false,          // Set a custom <a> title if required.
	            scrollImg: false,            // Set true to use image
	            activeOverlay: false,        // Set CSS color to display scrollUp active point, e.g '#00FFFF'
	            zIndex: 2147483647           // Z-Index for the overlay
	        });
	    });
})
();