function addMatchItems_v2(data) {
	function cleanMatchMarkers() {
		var overlays = map.getOverlays();
		for ( var m in overlays) {
			if (overlays[m] instanceof BMap.Marker
					&& overlays[m].getTitle() != '我的位置') {
				map.removeOverlay(overlays[m]);
			}
		}
	}

	if (data.length == 0) {
		if ($("#nomatch").length == 0) {
			$("#matchlist").children("#match").remove();
			createNoMatch();
			cleanMatchMarkers();
		}
	} else {
		$("#matchlist").children("#nomatch").remove();
		$("#matchlist").children("#match").remove();
		var ggpoints = [];
		for ( var idx in data) {
			ggPoint = new BMap.Point(data[idx].fields.poolroom.lng,
					data[idx].fields.poolroom.lat);
			ggpoints.push(ggPoint);
		}
		convertPoints(ggpoints, function(convertedPoints) {
			cleanMatchMarkers();
			if (data.length > 1)
				map.centerAndZoom('北京');
			for ( var idx in data) {
				matchobj = addMatchToList_v2(data[idx], convertedPoints[idx]);
				var titleobj = matchobj.find("span[name=title]");
				if (idx == 0 && data.length == 1) {
					// only one point
					var points = $(titleobj).attr("point").split(",");
					var point = new BMap.Point(points[0], points[1]);
					map.centerAndZoom(point,15);
				}
				createMatchMarker(idx, titleobj);
			}
			if (mypoint != null)
				updateDistance(mypoint);
			$(document).foundation();
		});
	}
}

function addMatchToList_v2(match, point) {
	var matchobj = jQuery('<div/>', {
		class : 'row',
		id : 'match'
	});
	detail_url = MATCH_URL.replace(/000/g, match.pk);
	contentTemplate = "<div class=\"large-2 columns\">"
			+ "<div class=\"row panel\">$starttime</div></div>"
			+ "<div class=\"large-7 columns\">"
			+ "<div class=\"row panel match-summary\">"
			+ "<div class=\"large-2 columns\"><img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/demo1-th.jpg\"></div>"
			+ "<div class=\"large-7 columns\">"
			+ "<div class=\"row\">"
			+ "<h5><span name=\"title\" point=\"$point\" match=\"$matchjsonstr\"><u>$poolroomname</u></span></h5>"
			+ "<a target=\"_blank\" href=\"" + detail_url + "\">详情</a>"
			+ "</div>"
			+ "<div class=\"row\">"
	equipment = "";
	if (match.fields.poolroom.flags.wifi)
		equipment += "<span class=\"ico_wifi\" title=\"公共区域WIFI\"></span>";
	if (match.fields.poolroom.flags.wifi_free)
		equipment += "<span class=\"ico_free_wifi\" title=\"公共区域WIFI\"></span>";
	if (match.fields.poolroom.flags.parking || match.fields.poolroom.flags.parking_free)
		equipment += "<span class=\"ico_parking\" title=\"停车场\"></span>";
	if (match.fields.poolroom.flags.cafeteria)
		equipment += "<span class=\"ico_restaurant\" title=\"餐饮服务\"></span>";
	if (match.fields.poolroom.flags.subway)
		equipment += "<span class=\"ico_bus\" title=\"地铁周边\"></span>";
	if (equipment != "") {
		contentTemplate += "<span class=\"icon_list\">";
		contentTemplate += "<div class=\"ico_none\">球房设施: </div>";
		contentTemplate += equipment;
		contentTemplate += "</span>";
	}
	contentTemplate += "</div><div class=\"row\" id=\"distance\"></div>" 
			+ "</div><div class=\"large-3 columns\">"
			+ "<div class=\"row\">已报名人数:</div>"
			+ "<div class=\"row\">76人</div>"
			+ "<div class=\"row\">"
			+ "<a href=\"#\" class=\"small radius button\">我要报名</a>"
			+ "</div>"
			+ "</div>"
			+ "</div>"
			+ "</div>"
			+ "<div class=\"large-3 columns panel\">"
			+ "<div class=\"row\"><h4>冠军奖励:</h4></div>";
	if (match.fields.bonus > 0)
		contentTemplate += "<div class=\"row\">现金: $bonus元</div>";
	if (match.fields.rechargeablecard > 0)
		contentTemplate += "<div class=\"row\">俱乐部充值卡: $rechargeablecard元</div>";
	if (match.fields.otherprize != null)
		contentTemplate += "<div class=\"row\">$otherprize</div>";
	contentTemplate += "<div class=\"row\">"
			+ "<span data-tooltip class=\"has-tip\" title=\"$rule\">比赛规则</span>"
			+ "&nbsp;&nbsp;&nbsp;&nbsp;"
			+ "<span data-tooltip class=\"has-tip\" title=\"$bonusdetail\">奖金设置</span></div>"
			+ "</div>";
	contentTemplate = contentTemplate.replace(/\$point/g,
			point.lng + "," + point.lat).replace(/\$matchjsonstr/g,
			objectToJsonString([ match ])).replace(/\$poolroomname/g,
			match.fields.poolroom.name).replace(/\$starttime/g,
			getFormattedTime2(match.fields.starttime))
			.replace(/\$bonusdetail/g, match.fields.bonusdetail)
			.replace(/\$bonus/g, match.fields.bonus)
			.replace(/\$rechargeablecard/g, match.fields.rechargeablecard)
			.replace(/\$otherprize/g, match.fields.otherprize).replace(/\$rule/g, match.fields.rule)
			.replace(/\$address/g, match.fields.poolroom.address).replace(/\$enrollfee/g, match.fields.enrollfee)
			.replace(/\$enrollfocalpoint/g, match.fields.enrollfocal);
	matchobj.append(contentTemplate);
	matchobj.appendTo('#matchlist');
	return matchobj;
}

function MyLocaiton(){
    // 默认停靠位置和偏移量
    this.defaultAnchor = BMAP_ANCHOR_TOP_LEFT;
    this.defaultOffset = new BMap.Size(10, 10);
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

R=6370996.81;//地球半径
function pi() {
	return Math.PI;
}
function distance(point1, point2) {
	return R*Math.acos(Math.cos(point1.lat*pi()/180 )*Math.cos(point2.lat*pi()/180)*Math.cos(point1.lng*pi()/180 -point2.lng*pi()/180)+
			Math.sin(point1.lat*pi()/180 )*Math.sin(point2.lat*pi()/180))
}

function formatDistance(distance) {
	if (distance < 1000) {
		return Math.floor(distance/100) * 100 + "米";
	} else {
		return Math.round(distance/100)/10 + "公里";	
	}
}

function updateDistance(mypoint) {
	$("#matchlist").children("#match").each(function() {
		var pointstr = $(this).find("span[name=title]").attr("point").split(",");
		var point = new BMap.Point(pointstr[0], pointstr[1]);
		var distanceobj = $(this).find("#distance");
		var html = "<h5>距离我: <strong>" + formatDistance(distance(mypoint, point)) + "</strong></h5>";
		distanceobj.append(html);
	});
}