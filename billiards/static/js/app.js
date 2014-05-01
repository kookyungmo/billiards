function setGetParameter(url, paramName, paramValue)
{
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
	window.location = setGetParameter(url, 'returnurl', window.location.pathname + window.location.search);
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
			cellphone: /^(1(([35][0-9])|(47)|[8][012356789]))\d{8}$/,
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