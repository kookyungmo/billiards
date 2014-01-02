function hasOwnProperty(obj, prop) {
    var proto = obj.__proto__ || obj.constructor.prototype;
    return (prop in obj) &&
        (!(prop in proto) || proto[prop] !== obj[prop]);
}

if ( Object.prototype.hasOwnProperty ) {
    var hasOwnProperty = function(obj, prop) {
        return obj.hasOwnProperty(prop);
    }
}

function isAuth() {
	return AUTH == 1;
}

function addMatchItems_v2(data) {
	if (data.length == 0) {
		if ($("#nomatch").length == 0) {
			$("#matchlist").children("#match").remove();
			createNoMatch();
			cleanNonLocationMarkers();
		}
	} else {
		$("#matchlist").children("#nomatch").remove();
		$("#matchlist").children("#match").remove();
		cleanNonLocationMarkers();
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
	contentTemplate ="<div class=\"row\">"
			+ "<div class=\"small-12 large-2 columns\">"
//                        + "<ul class=\"pricing-table\">"
//                        + "<li class=\"title\"><font size=+1>$starttimedate</font></li>"
//                        + "<li class=\"price\">$starttimeweekday</li>"
//                        + "<li class=\"title\"><font size=+1>$starttimehour</font></li>"
//			+ "</ul>"
			+ "<ul class=\"calendar\"><em>$starttimedate</em>$starttimehour<em>$starttimeweekday</em></ul>"
			+ "</div>"

			+ "<div class=\"small-12 large-7 columns\">"
			+ "<div class=\"row\">"
			+ "<div class=\"small-12 columns\">"
			+ "<div class=\"columns panel clickable\" style=\"overflow:auto;\">"
			+ "<div class=\"small-4 medium-4 columns\">"
			
			+ "<ul class=\"clearing-thumbs\" data-clearing>"
			+ " <li><a class=\"th\" href=\"http://api.map.baidu.com/staticimage?center=116.403874,39.914888&width=600&height=400&zoom=15\"><img data-caption=\"caption 3 here\" src=\"http://api.map.baidu.com/staticimage?center=116.403874,39.914888&width=300&height=200&zoom=11\"></a></li>"

			+ "</ul>"
			+ "</div>"

			+ "<div class=\"small-8 medium-8 columns\">"
			+ "<div class=\"row\">"
			+ "<p><font size=><span name=\"title\" point=\"$point\" match=\"$matchjsonstr\" style=\"color:#EB6100\"><strong>$poolroomname&nbsp;&nbsp;&nbsp;</strong></a></span>"
			+ "<a href=\"" + detail_url + "\">比赛详情 >></a></font></p>"
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
		contentTemplate += "<div class=\"ico_none\"><font size=-1>球房设施: </font></div>";
		contentTemplate += equipment;
		contentTemplate += "</span>";
	}
	contentTemplate += "</div><div class=\"row\" id=\"distance\"></div>" 
			+ "</div>"
			+ "</div>"
			+ "</div>"
			+ "</div>"
			+ "</div>"
            + "<div class=\"small-12 large-3 columns\">"
			+ "<ul class=\"pricing-table\">"
			+ "<li class=\"title\"><font size=+1>"
	if (match.fields.bonus > 0)
		contentTemplate += "现金: $bonus元 &nbsp;&nbsp"
	if (match.fields.rechargeablecard > 0)
		contentTemplate += "俱乐部充值卡: $rechargeablecard元";
	if (match.fields.otherprize != null)
		contentTemplate += "$otherprize</font></li>";
	contentTemplate += ""
			+ "<a href=\"#\" data-reveal-id=\"rule\"><font size=-1>比赛规则 >></font></a>"
			+ "&nbsp;&nbsp;&nbsp;&nbsp;"
			+ "<li id=\"rule\" class=\"reveal-modal\" data-reveal>"
			+ " <p>$rule</p>"
			+ " <a class=\"close-reveal-modal\">&#215;</a>"
			+ "</li>"
            + "<a href=\"#\" data-reveal-id=\"bonusdetail\"><font size=-1>奖金设置 >></font></a>"
			+ "<li id=\"bonusdetail\" class=\"reveal-modal\" data-reveal>"
			+ " <p>$bonusdetail</p>"
			+ " <a class=\"close-reveal-modal\">&#215;</a>"
			+ "</li></ul>";
	if (isAuth())
		if ( hasOwnProperty(match.fields, 'enrolled') ) 
			contentTemplate += "<h3>已报名。</h3>";
		else
			contentTemplate += "<a href=\"javascript:void(0);\" id=\"enroll\" match='" + match.pk + "' class=\"button expand\">我要报名比赛</a>";
	else
		contentTemplate	+= "<a href=\"javascript:void(0);\" data-reveal-id=\"quickLogin\" class=\"button expand\">我要报名比赛</a>";
	contentTemplate += "</div>"
			+ "</div>";

	contentTemplate = contentTemplate.replace(/\$point/g,
			point.lng + "," + point.lat).replace(/\$matchjsonstr/g,
			objectToJsonString([ match ])).replace(/\$poolroomname/g,
			match.fields.poolroom.name)
			.replace(/\$starttimeweekday/g,getFormattedTimeToWeekDay(match.fields.starttime))
			.replace(/\$starttimedate/g,getFormattedTime(match.fields.starttime))
			.replace(/\$starttimehour/g,getFormattedTime2(match.fields.starttime))
			.replace(/\$starttime/g,getFormattedTimeToDate(match.fields.starttime))
			.replace(/\$bonusdetail/g, match.fields.bonusdetail)
			.replace(/\$bonus/g, match.fields.bonus)
			.replace(/\$rechargeablecard/g, match.fields.rechargeablecard)
			.replace(/\$otherprize/g, match.fields.otherprize).replace(/\$rule/g, match.fields.rule)
			.replace(/\$address/g, match.fields.poolroom.address).replace(/\$enrollfee/g, match.fields.enrollfee)
			.replace(/\$enrollfocalpoint/g, match.fields.enrollfocal);
	matchobj.append(contentTemplate);
	matchobj.appendTo('#matchlist');
	$("#match #enroll").click(function(){
		matchEnroll($(this).parent(), $(this).attr('match'));
	});
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
		var html = "<h4>距离我: <strong>" + formatDistance(distance(mypoint, point)) + "</strong></h4>";
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
	url = POOLROOM_URL;
	detail_url = url.replace(/000/g, poolroom.pk);
	contentTemplate = "<div class=\"row\">"

			+ "<div class=\"small-12 large-2 columns\">"
			+ "<ul class=\"pricing-table\">"
			+ "<li class=\"title\"><font size=+1><strong>距离我：</strong></font></li>"
			+ "<li class=\"price\">$distance</li>"
			+ "</ul></div>"

			+ "<div class=\"small-12 large-10 columns panel clickable\">"
			+ "<div class=\"small-4 columns\"><img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/demo1-th.jpg\"></div>"
			+ "<div class=\"small-8 columns\">"
			+ "<div class=\"row\">"
			+ "<h5><span name=\"title\" point=\"$point\"><u><a href=\"" + detail_url + "\">$poolroomname</a></u></span></h5>"
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
	contentTemplate += "</div><div class=\"row\"><h6 class=\"subheader\">地址: $address</h6></div>";
	contentTemplate += "<div class=\"row\"><h6 class=\"subheader\">电话: $tel</h6></div>";
	contentTemplate += "<div class=\"row\"><h6 class=\"subheader\">营业时间: $hour</h6></div>";
	contentTemplate += "</div></div></div>";

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
				var content = "<h6 style = color:#EB6100><strong>" + poolroom.fields.name + "</strong></h6>";
				content += "<p><font size=-2>地址: <strong>"
					+ poolroom.fields.address
					+ "</strong></font></p><p><font size=-2>营业时间: <strong>"
					+ poolroom.fields.businesshours
					+ "</strong></font></p>";
				if (poolroom.fields.distance != null) {
					content += "<p>距离我: <strong>"
						+ formatDistance(poolroom.fields.distance * 1000) + "</strong></p>";
				}
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

function createInfo(text) {
	if ($("#info .subheader").length == 0) {
		var infoobj = jQuery('<div/>', {
			class : 'panel',
			id : 'info'
		});
		infoobj.append("<h3 class=\"subheader\">" + text + "</h3>");
		infoobj.appendTo('#content');
	} else {
		$("#info .subheader").text(text);
	}
}

function loadingPoolroom(distance, mypoint) {
	createInfo("正在加载附近的球房...");
	url = NEARBY_URL;
    $.ajax({
		url : url.replace(/00\.00/g, mypoint.lat).replace(/11\.11/g, mypoint.lng)
				.replace(/00/g, distance),
		data : {'f':'json'},
		dataType : 'json',
		success : function(data)
		{
			if (data.length == 0) {
				$("#info .subheader").text("真遗憾，您附近没有我们收录的球房。");
			} else {
				$("#info").remove();
				addPoolroom(data, mypoint);
			}
		},
		error: function (xhr, ajaxOptions, thrownError) {
			$("#info .subheader").text("无法获取周边的球房，请刷新重试。");
	     }
	});
}

function matchEnroll(objdiv, id) {
	url = ENROLL_URL;
	$.ajax({
		url : url.replace(/000/g, id),
		dataType : 'json',
		success : function(data)
		{
			objdiv.children("#enroll").remove();
			objdiv.append("<h3>报名成功。</h3>");
			if (data.info_missing) {
				$('#userInfoForm').foundation('reveal', 'open');
			}
		},
		error: function (xhr, ajaxOptions, thrownError) {
			if (xhr.status == 403) {
				$('#quickLogin').foundation('reveal', 'open');
		    }
	     }
	});
}
