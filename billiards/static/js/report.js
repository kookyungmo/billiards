function refreshUserData(data) {
	$("#reporttable").children().remove();
	if (data.length > 0) {
		var tableobj = jQuery('<table/>', {
		});
		contentTemplate ="<thead>"
			+ "<tr>"
			+ "<th width=\"200\">用户id</th>"
			+ "<th width=\"300\">关注日期</th>"
			+ "<th width=\"300\">是否首次关注</th>"
			+ "<th width=\"300\">是否已取消关注</th>"
			+ "<th width=\"300\">取消关注日期</th>"
			+ "</tr></thead><tbody>";
		for (idx in data) {
			contentTemplate += "<tr>"
				+ "<td>" + data[idx].fields.userid + "</td>"
				+ "<td>" + getFormattedTimeToDate(data[idx].fields.receivedtime) + "</td>"
				+ "<td>" + (data[idx].fields.firstjoin ? "是" : "否") + "</td>";
			if (data[idx].fields.unsubscribed == true) {
				contentTemplate += "<td>是</td>"
					+ "<td>" + data[idx].fields.unsubscribedDate + "</td>";
			} else {
				contentTemplate += "<td>否</td>"
					+ "<td>" + '' + "</td>";
			}
			contentTemplate += "</tr>";
		}
		contentTemplate += "</tbody>";
		tableobj.append(contentTemplate);
		tableobj.appendTo('#reporttable');
	} else {
		var preobj = jQuery('<pre/>', {
		});
		content = "<code class=\"language-html\"><h2>此时间段没有新关注用户。</h2></code>";
		preobj.append(content);
		preobj.appendTo('#reporttable');
	}
}

function refreshMessageData(data) {
	$("#reporttable").children().remove();
	if (data.length > 0) {
		var tableobj = jQuery('<table/>', {
		});
		contentTemplate ="<thead>"
			+ "<tr>"
			+ "<th width=\"200\">用户id</th>"
			+ "<th width=\"500\">发送日期</th>"
			+ "<th width=\"400\">消息类别</th>"
			+ "<th width=\"400\">消息内容</th>"
			+ "<th width=\"800\">Raw消息内容</th>"
			+ "</tr></thead><tbody>";
		for (idx in data) {
			contentTemplate += "<tr>"
				+ "<td>" + data[idx].fields.userid + "</td>"
				+ "<td>" + getFormattedTimeToDate(data[idx].fields.receivedtime) + "</td>";
			if (data[idx].fields.eventtype == 'location')
				type = "地理位置";
			else if (data[idx].fields.eventtype == 'text')
				type = "文字消息";
			else
				type = "其他消息";
			contentTemplate += "<td>" + type + "</td>"
				+ "<td>" + (data[idx].fields.keyword !== "" ? data[idx].fields.keyword : "&nbsp;") + "</td>"
				+ "<td>" + data[idx].fields.message + "</td>";
			contentTemplate += "</tr>";
		}
		contentTemplate += "</tbody>";
		tableobj.append(contentTemplate);
		tableobj.appendTo('#reporttable');
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
			callback(data);
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
