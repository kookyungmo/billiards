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
			
			+ "<ul class=\"clearing-thumbs clearing-feature\" data-clearing>"
			+ " <li class=\"clearing-featured-img\"><a class=\"th\" href=\"http://api.map.baidu.com/staticimage?center=$point&width=600&height=400&zoom=18&scale=2&markers=$point&markerStyles=-1,http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png\"><img data-caption=\"MapShot\" src=\"http://api.map.baidu.com/staticimage?center=$point&width=100&height=62&zoom=16&scale=2&markers=$point&markerStyles=-1,http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png\"></a></li>"
			+ "<li><a class=\"th\" href=\"http://placehold.it/200x200\"><img src=\"http://placehold.it/200x200\"></a></li>"
			+ "</ul>"
			+ "</div>"

			+ "<div class=\"small-8 medium-8 columns\">"
			+ "<div class=\"row\">"
			+ "<p><font size=><span name=\"title\" point=\"$point\" match=\"$matchjsonstr\" style=\"color:#EB6100\"><strong>$poolroomname&nbsp;&nbsp;&nbsp;</strong></a></span>"
			+ "<a href=\"" + detail_url + "\">比赛详情 &raquo</a></font></p>"
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
			+ "<a href=\"#\" data-reveal-id=\"rule\"><font size=-1>比赛规则 &raquo</font></a>"
			+ "&nbsp;&nbsp;&nbsp;&nbsp;"
			+ "<li id=\"rule\" class=\"reveal-modal\" data-reveal>"
			+ " <p>$rule</p>"
			+ " <a class=\"close-reveal-modal\">&#215;</a>"
			+ "</li>"
            + "<a href=\"#\" data-reveal-id=\"bonusdetail\"><font size=-1>奖金设置 &raquo</font></a>"
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
		var distanceobj = $(this).find("div[id=distance]");
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
			+ "<div class=\"small-4 large-4 columns\">"
			+ "<ul class=\"clearing-thumbs clearing-feature\" data-clearing>"
			+ " <li class=\"clearing-featured-img\"><a class=\"th\" href=\"http://api.map.baidu.com/staticimage?center=$point&width=900&height=600&zoom=18&scale=2&markers=$point&markerStyles=-1,http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png\"><img data-caption=\"MapShot\" src=\"http://api.map.baidu.com/staticimage?center=$point&width=100&height=62&zoom=16&scale=2&markers=$point&markerStyles=-1,http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png\"></a></li>"
			+ "</ul>"
                        + "</div>"
			+ "<div class=\"small-8 large-8 columns\">"
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
				$(document).foundation();
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

function getChallenges(point) {
	url = CHALLENGE_URL;
	if (point != null) {
		url = CHALLENGE_WITH_DISTANCE_URL;
		url = url.replace(/00\.00/g, point.lat).replace(/11\.11/g, point.lng);
	}
	$.ajax({
		url : url,
		data : {'f':'json'},
		dataType : 'json',
		success : function(data)
		{
			if (data.length == 0) {
				$("#info .subheader").text("真遗憾，暂时没有俱乐部发布的约球信息。");
			} else {
				$("#info").remove();
				addChallenges(data, point);
			}
		},
		error: function (xhr, ajaxOptions, thrownError) {
			$("#info .subheader").text("无法获取约球信息，请刷新重试。");
	     }
	});
}

function addChallengeToList(challenge, point, mypoint) {
	var challengeobj = jQuery('<div/>', {
		class : 'row',
		id : 'challenge'
	});
	url = POOLROOM_URL;
	detail_url = url.replace(/000/g, challenge.fields.issuer.id);
	contentTemplate = "<div class=\"small-12 columns\">"
			+ "<div class=\"row\">"
			+ "<div class=\"small-4 large-2 columns\">"
			+ "<ul class=\"pricing-table\">"
			+ "<li class=\"title\"><font size=+1><strong>距离我：</strong></font></li>"
			+ "<li class=\"price\">$distance</li>"
			+ "</ul></div>"
			+ "<div class=\"small-8 large-10 columns panel\">"
			+ "<div class=\"row\">"
			+ "<div class=\"small-5 medium-2 center columns\"><img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/demo1-th.jpg\"></div>"
			+ "<div class=\"small-7 medium-10 columns\">"
			+ "<h5><span name=\"title\" point=\"$point\"><u><a href=\"" + detail_url + "\">$poolroomname</a></u></span></h5>"
			+ "<div class=\"row\">"
	equipment = "";
	if (challenge.fields.issuer.flags.wifi)
		equipment += "<span class=\"ico_wifi\" title=\"公共区域WIFI\"></span>";
	if (challenge.fields.issuer.flags.wifi_free)
		equipment += "<span class=\"ico_free_wifi\" title=\"公共区域WIFI\"></span>";
	if (challenge.fields.issuer.flags.parking || challenge.fields.issuer.flags.parking_free)
		equipment += "<span class=\"ico_parking\" title=\"停车场\"></span>";
	if (challenge.fields.issuer.flags.cafeteria)
		equipment += "<span class=\"ico_restaurant\" title=\"餐饮服务\"></span>";
	if (challenge.fields.issuer.flags.subway)
		equipment += "<span class=\"ico_bus\" title=\"地铁周边\"></span>";
	if (equipment != "") {
		contentTemplate += "<span class=\"icon_list\">";
		contentTemplate += "<div class=\"ico_none\">球房设施: </div>";
		contentTemplate += equipment;
		contentTemplate += "</span>";
	}
	contentTemplate += "</div></div></div>";
	contentTemplate += "<hr><div class=\"row\">"
		+ "<div class=\"small-5 medium-2 columns\">" 
		+ "<ul class=\"pricing-table\"><li class=\"title\">开始时间</li><li class=\"bullet-item\">$starttime</li>"
		+ "<li class=\"title\">过期时间</li><li class=\"bullet-item\">$endtime</li></ul>"
		+ "</div>"
		+ "<div class=\"small-7 medium-10 columns\">"
		+ "<p>一名<code>$level $nick</code>发起约球</p>"
		+ "<div class=\"row\">" 
		+ "<div class=\"small-12 medium-4 columns\">"
		+ "<p>比赛类型: <code>$tabletype</code></p></div>"
		+ "<div class=\"small-12 medium-8 columns\"><p>比赛方式: <code>$rule</code></p></div></div>";
	
	if (challenge.fields.applied) {
		contentTemplate += "<a class=\"button radius disabled\">您已经申请, 请等待俱乐部的确认。</a>";
	} else {
		if (challenge.fields.status == 'waiting') {
			if (isAuth()) {
				contentTemplate += "<a id=\"enroll\" challenge=\"" + challenge.pk + "\" class=\"button radius\">我要应战</a>";
			} else
				contentTemplate += "<a href=\"javascript:void(0);\" data-reveal-id=\"quickLogin\" class=\"button radius\">我要应战</a>";
		} else if (challenge.fields.status == 'matched')
			contentTemplate += "<a class=\"button radius disabled\">已经匹配</a>";
		else if (challenge.fields.status == 'expired') {
			contentTemplate += "<a class=\"button radius disabled\">已经过期</a>";
		}
	}
	contentTemplate += "</div></div></div>";

	contentTemplate = contentTemplate.replace(/\$point/g, point.lng + "," + point.lat)
			.replace(/\$distance/g, (mypoint == null ? "无法获取你的位置" : formatDistance(distance(mypoint, point))))
			.replace(/\$poolroomname/g, challenge.fields.issuer.name)
			.replace(/\$starttime/g, getSmartTime(challenge.fields.starttime))
			.replace(/\$endtime/g, getSmartTime(challenge.fields.expiretime))
			.replace(/\$level/g, challenge.fields.level)
			.replace(/\$nick/g, (challenge.fields.issuer_nickname == null ? "" : challenge.fields.issuer_nickname))
			.replace(/\$tabletype/g, challenge.fields.tabletype)
			.replace(/\$rule/g, challenge.fields.rule);
	challengeobj.append(contentTemplate);
	challengeobj.appendTo('#content');
	$("#content #enroll").click(function(){
		applyChallenge($(this).parent(), $(this).attr('challenge'));
	});
	return challengeobj;
}

function getSmartTime(datetime) {
	if (moment(datetime).format("MM-DD-YYYY") == moment().format("MM-DD-YYYY")) {
		return getFormattedTime2(datetime);
	}
	return getFormattedTimeToDate(datetime);
}

function addChallenges(challenges, mypoint) {
	for ( var idx in challenges) {
		point = new BMap.Point(challenges[idx].fields.issuer.lng,
				challenges[idx].fields.issuer.lat);
		addChallengeToList(challenges[idx], point, mypoint);
	}
	$(document).foundation();
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
