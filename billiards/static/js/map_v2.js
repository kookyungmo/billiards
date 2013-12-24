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
		cleanMatchMarkers();
		if (data.length > 1)
			map.centerAndZoom('北京');
		for ( var idx in data) {
			point = new BMap.Point(data[idx].fields.poolroom.lng,
					data[idx].fields.poolroom.lat);
			matchobj = addMatchToList_v2(data[idx], point);
			var titleobj = matchobj.find("span[name=title]");
			if (idx == 0 && data.length == 1) {
				// only one point
				map.centerAndZoom(point,15);
			}
			createMatchMarker(idx, titleobj);
		}
		if (mypoint != null)
			updateDistance(mypoint);
		$(document).foundation();
	}
}

function addMatchToList_v2(match, point) {
	var matchobj = jQuery('<div/>', {
		class : 'row',
		id : 'match'
	});
	detail_url = MATCH_URL.replace(/000/g, match.pk);
	contentTemplate ="<div class=\"row\">"// "<div class=\"small-2 columns\">"
			+ "<div class=\"row panel\" style=\"position:relative;left:25px;width:90%;\">$starttime &nbsp; &nbsp; 冠军奖励 &nbsp;"
        if (match.fields.bonus > 0)
                contentTemplate += "现金: $bonus元 &nbsp;&nbsp;";
        if (match.fields.rechargeablecard > 0)
                contentTemplate += "俱乐部充值卡: $rechargeablecard元 &nbsp;&nbsp;";
        if (match.fields.otherprize != null)
                contentTemplate += "$otherprize";
		contentTemplate += "<span data-tooltip class=\"has-tip\" title=\"$bonusdetail\">奖金设置</span>"
        contentTemplate += "</div></div>"
			+ "<div class=\"small-8 columns\">"
			+ "<div class=\"row panel clickable\" style=\"height:150px;overflow:auto;\">"
//			+ "<div class=\"small-4 medium-2 columns\"><img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/demo1-th.jpg\"></div>"
			+ "<div class=\"small-8 medium-8 columns\">"
			+ "<div class=\"row\">"
			+ "<h5><span name=\"title\" point=\"$point\" match=\"$matchjsonstr\" style=\"color:#EB6100\"><strong>$poolroomname</strong></span>"
			+"<span data-tooltip class=\"has-tip\" title=\"$rule\">&nbsp;比赛规则</span>"
			+ "&nbsp; &nbsp; <a href=\"" + detail_url + "\">比赛详情</a></h5>"
			+ "</div>"
			+ "<br>"
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
			+ "</div><div class=\"small-12 medium-3 columns\">"
			+ "<div class=\"row\">已报名人数:</div>"
			+ "<div class=\"row\">76人</div>"
			+ "<div class=\"row\">"
			+ "<a href=\"#\" class=\"small radius button\">我要报名</a>"
			+ "</div>"
			+ "</div>"
			+ "</div>"
			+ "</div>"
			+ "<div class=\"small-4 columns panel\" style=\"height:150px;overflow:auto;\">"
			+ "<div class=\"row\"><strong>冠军奖励:</strong></div>";
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

function initialMap(id) {
	var map = new BMap.Map(id);
	map.addControl(new BMap.NavigationControl({anchor: BMAP_ANCHOR_TOP_RIGHT, type: BMAP_NAVIGATION_CONTROL_SMALL}));
    map.enableScrollWheelZoom(true);
    return map;
}

function addMyLocation(point) {
	var marker = addMarker(point, STATIC_URL + "/images/location.png");
    marker.addEventListener("mouseover",function(){
        marker.setAnimation(BMAP_ANIMATION_BOUNCE);
    });
    marker.addEventListener("mouseout",function(){
        marker.setAnimation(null); 
    });
    marker.setTitle('我的位置');
    return marker;
}

function addCustomToolbar(map, point) {
	MyLocaiton.prototype = new BMap.Control();
    MyLocaiton.prototype.initialize = function(map){

	    var div = document.createElement("div");
	    div.appendChild(document.createTextNode("我的位置"));
	
	    div.style.cursor = "pointer";
	    div.style.border = "1px solid gray";
	    div.style.backgroundColor = "white";
	
	    div.onclick = function(e){
	    	map.centerAndZoom(point,12);
	    }
	    map.getContainer().appendChild(div);
	    return div;
    }

    var myCtrl = new MyLocaiton();
    map.addControl(myCtrl);
}

function addPoolroom(data, mypoint) {	
	if (data.length > 1)
		map.panTo(mypoint);
	for ( var idx in data) {
		point = new BMap.Point(data[idx].fields.lng_baidu,
				data[idx].fields.lat_baidu);
		poolroomobj = addPoolroomToList(data[idx], point);
		createPoolroomMarker(idx, poolroomobj, data[idx], point);
	}
}

function addPoolroomToList(poolroom, point) {
	var poolroomobj = jQuery('<div/>', {
		class : 'row',
		id : 'poolroom'
	});
	detail_url = POOLROOM_URL.replace(/000/g, poolroom.pk);
	contentTemplate = "<div class=\"small-12 columns clickable\">"
			+ "<div class=\"row panel poolroom-detail\">"
			+ "<div class=\"small-4 columns\"><img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/demo1-th.jpg\"></div>"
			+ "<div class=\"small-8 columns\">"
			+ "<div class=\"row\">"
			+ "<h3><span name=\"title\" point=\"$point\"><u>$poolroomname</u></span></h3>"
			+ "</div>"
			+ "<div class=\"row\">"
	equipment = "";
	if (poolroom.fields.flags.wifi)
		equipment += "<span class=\"ico_wifi\" title=\"公共区域WIFI\"></span>";
	if (poolroom.fields.flags.wifi_free)
		equipment += "<span class=\"ico_free_wifi\" title=\"公共区域WIFI\"></span>";
	if (poolroom.fields.flags.parking || poolroom.fields.flags.parking_free)
		equipment += "<span class=\"ico_parking\" title=\"停车场\"></span>";
	if (poolroom.fields.flags.cafeteria)
		equipment += "<span class=\"ico_restaurant\" title=\"餐饮服务\"></span>";
	if (poolroom.fields.flags.subway)
		equipment += "<span class=\"ico_bus\" title=\"地铁周边\"></span>";
	if (equipment != "") {
		contentTemplate += "<span class=\"icon_list\">";
		contentTemplate += "<div class=\"ico_none\">球房设施: </div>";
		contentTemplate += equipment;
		contentTemplate += "</span>";
	}
	contentTemplate += "</div><div class=\"row\"><h3 class=\"subheader\">地址: $address</h3></div>";
	contentTemplate += "<div class=\"row\"><h3 class=\"subheader\">电话: $tel</h3></div>";
	contentTemplate += "<div class=\"row\"><h3 class=\"subheader\">营业时间: $hour</h3></div>";
	contentTemplate += "<div class=\"row\"><h3 class=\"subheader\">距离我: <strong>$distance</strong></h3></div>";
	contentTemplate += "</div>";
	contentTemplate = contentTemplate.replace(/\$point/g,
			point.lng + "," + point.lat)
			.replace(/\$poolroomname/g, poolroom.fields.name)
			.replace(/\$address/g, poolroom.fields.address)
			.replace(/\$tel/g, poolroom.fields.tel)
			.replace(/\$hour/g, poolroom.fields.businesshours)
			.replace(/\$distance/g, formatDistance(poolroom.fields.distance * 1000));
	poolroomobj.append(contentTemplate);
	poolroomobj.appendTo('#poolroomlist');
	return poolroomobj;	
}

var poolroomInfo = function(marker, poolroom) {
	(function() {
		var info = {
			open : function(type, target) {
				var content = "<h3 style = color:#EB6100><strong>" + poolroom.fields.name + "</strong></h3>";
				content += "<p>地址: <strong>"
					+ poolroom.fields.address
					+ "</strong></p><p>营业时间: <strong>"
					+ poolroom.fields.businesshours
					+ "</strong></p><p>距离我: <strong>"
					+ formatDistance(poolroom.fields.distance * 1000) + "</strong></p>";
				var infoWindow = new BMap.InfoWindow(content);
				marker.openInfoWindow(infoWindow);
				infoWindow.redraw();
			}
		}
		info.open();
	})();
};

function addPoolroomMarker(i, point, poolroom) {
	var mk = addMarker(point, STATIC_URL + "/images/marker.png");
	mk.addEventListener("click", function() {
		poolroomInfo(mk, poolroom);
	});
	return mk;
}

function createPoolroomMarker(i, obj, poolroom, point) {
	var marker = addPoolroomMarker(i, point, poolroom);
	(function(){
		$(obj).click(
			function(event) {
				var link = $(obj);
				var clickingobj = $(event.target);
				if (clickingobj[0].tagName == 'A') {
					//TODO catch click event on link
				} else {
					poolroomInfo(marker, poolroom);
				}
			});
	})();
}
