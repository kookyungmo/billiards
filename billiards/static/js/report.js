function refreshUserData(url, startdate, enddate, messages) {
	$("#reporttable").children().remove();
	data = messages.data;
	if (data.length > 0) {
		var tableobj = jQuery('<table/>', {
		});
		contentTemplate ="<thead>"
			+ "<tr>"
			+ "<th width=\"200\">微信帐号</th>"
			+ "<th width=\"200\">用户id</th>"
			+ "<th width=\"300\">关注日期</th>"
			+ "<th width=\"300\">是否首次关注</th>"
			+ "<th width=\"300\">是否已取消关注</th>"
			+ "<th width=\"300\">取消关注日期</th>"
			+ "</tr></thead><tbody>";
		for (idx in data) {
			contentTemplate += "<tr>"
				+ "<td>" + data[idx].fields.target + "</td>"
				+ "<td>" + data[idx].fields.userid + "</td>"
				+ "<td>" + getFormattedTimeToDate(data[idx].fields.receivedtime) + "</td>"
				+ "<td>" + (data[idx].fields.firstjoin ? "是" : "否") + "</td>";
			if (data[idx].fields.unsubscribed == true) {
				contentTemplate += "<td>是</td>"
					+ "<td>" + getFormattedTimeToDate(data[idx].fields.unsubscribedDate) + "</td>";
			} else {
				contentTemplate += "<td>否</td>"
					+ "<td>" + '' + "</td>";
			}
			contentTemplate += "</tr>";
		}
		contentTemplate += "</tbody>";
		tableobj.append(contentTemplate);
		tableobj.appendTo('#reporttable');
		var ulobj = jQuery('<ul/>', {
			class : 'pagination'
		});
		contentTemplate = "";
		for (i = 1; i <= messages.count; i++) {
			contentTemplate += "<li ";
			if (messages.page == i) {
				contentTemplate += "class=\"current\"";
			}
			contentTemplate += "><a href=\"javascript:void(0);\">" + i + "</a></li>";
		}
		ulobj.append(contentTemplate);
		ulobj.appendTo('#reporttable');
		$('#reporttable ul li a').click(function(){
			pageurl = setGetParameter(url, 'page', $(this).text());
			getReportData(pageurl, startdate, enddate, refreshUserData);
		});
	} else {
		var preobj = jQuery('<pre/>', {
		});
		content = "<code class=\"language-html\"><h2>此时间段没有新关注用户。</h2></code>";
		preobj.append(content);
		preobj.appendTo('#reporttable');
	}
}

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

function refreshMessageData(url, startdate, enddate, messages) {
	$("#reporttable").children().remove();
	data = messages.data;
	if (data.length > 0) {
		var tableobj = jQuery('<table/>', {
		});
		contentTemplate ="<thead>"
			+ "<tr>"
			+ "<th width=\"200\">微信帐号</th>"
			+ "<th width=\"200\">用户id</th>"
			+ "<th width=\"500\">发送日期</th>"
			+ "<th width=\"400\">消息类别</th>"
			+ "<th width=\"400\">消息内容</th>"
			+ "<th width=\"800\">Raw消息内容</th>"
			+ "</tr></thead><tbody>";
		for (idx in data) {
			contentTemplate += "<tr>"
				+ "<td>" + data[idx].fields.target + "</td>"
				+ "<td>" + data[idx].fields.userid + "</td>"
				+ "<td>" + getFormattedTimeToDate(data[idx].fields.receivedtime) + "</td>";
			contentTemplate += "<td>" + data[idx].fields.eventtype + "</td>"
				+ "<td>" + (data[idx].fields.keyword !== "" ? data[idx].fields.keyword : "&nbsp;") + "</td>"
				+ "<td>" + data[idx].fields.message + "</td>";
			contentTemplate += "</tr>";
		}
		contentTemplate += "</tbody>";
		tableobj.append(contentTemplate);
		tableobj.appendTo('#reporttable');
		var ulobj = jQuery('<ul/>', {
			class : 'pagination'
		});
		contentTemplate = "";
		for (i = 1; i <= messages.count; i++) {
			contentTemplate += "<li ";
			if (messages.page == i) {
				contentTemplate += "class=\"current\"";
			}
			contentTemplate += "><a href=\"javascript:void(0);\">" + i + "</a></li>";
		}
		ulobj.append(contentTemplate);
		ulobj.appendTo('#reporttable');
		$('#reporttable ul li a').click(function(){
			pageurl = setGetParameter(url, 'page', $(this).text());
			getReportData(pageurl, startdate, enddate, refreshMessageData);
		});
	} else {
		var preobj = jQuery('<pre/>', {
		});
		content = "<code class=\"language-html\"><h2>此时间段没有用户发送的消息。</h2></code>";
		preobj.append(content);
		preobj.appendTo('#reporttable');
	}
}

function hookReportForm(callback) {
	$("#reportForm").on('valid', function() {
		startdate = moment($("#startdate").val()).tz(TIMEZONE);
		enddate = moment($("#enddate").val()).tz(TIMEZONE);
		getReportData(REPORT_URL, startdate, enddate, callback);
	});
	initialMomentTZ();
}

function getReportData(url, startdate, enddate, callback) {
	$("#errorMsg").addClass("hide");
	$.ajax({
		data : {
			'startdate': startdate.valueOf(),
			'enddate': enddate.valueOf(),
			},
			url : url,
			type: 'POST',
		dataType : 'json',
		success : function(data) {
			callback(url, startdate, enddate, data);
		},
		error : function(jqXHR, textStatus, errorThrown) {
			console.log(textStatus, errorThrown);
			$("#errorMsg .alert-box").text("网络错误，请重试。");
			$("#errorMsg").removeClass("hide");
		}
	});
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
