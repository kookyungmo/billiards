function getFormattedTime(timestr) {
	return moment(timestr).lang('zh_CN').format('MMMM Do, h:mm a')
}

function getFormattedTime2(timestr) {
	return moment(timestr).lang('zh_CN').format('h:mm a')
}

var matchInfo = function(marker, name, matches) {
	(function() {
		var info = {
			open : function(type, target) {
				var content = "<h3 style = color:#EB6100><strong>" + name + "</strong></h3>";
				for ( var idx in matches) {
					content += "<p><p/>地址: "
							+ matches[idx].fields.poolroom.address
							+ "<p><p/><strong>奖金: "
							+ matches[idx].fields.bonus
							+ "<br/>"
							+ "</strong><br/><strong>比赛时间: "
							+ getFormattedTime(matches[idx].fields.starttime) + "</strong></p>";
				}
				var infoWindow = new BMap.InfoWindow(content);
				marker.openInfoWindow(infoWindow);
				infoWindow.redraw();
			}
		}
		info.open();
	})();
};

function addMarker(point, iconpath) {
	var icon = new BMap.Icon(iconpath, new BMap.Size(39, 55), {
		anchor : new BMap.Size(15, 53),
		infoWindowAnchor : new BMap.Size(15, 0)
	});
	var marker = new BMap.Marker(point, {
		icon : icon
	});
	map.addOverlay(marker);
	return marker;
}

function addMatchMarker(i, point, match) {
	var mk = addMarker(point, STATIC_URL + "/images/marker.png");
	mk.addEventListener("click", function() {
		matchInfo(mk, match[0].fields.poolroom.name, match);
	});
	return mk;
}

var convertCallback;
var callback = function(xyResults) {
	var convertedPoints = [];
	var xyResult = null;
	for ( var index in xyResults) {
		xyResult = xyResults[index];
		if (xyResult.error != 0) {
			continue; //TODO better error handling
		}
		var point = new BMap.Point(xyResult.x, xyResult.y);
		convertedPoints.push(point);
	}
	if (convertCallback != null)
		convertCallback(convertedPoints);
}
function convertPoints(points, myConvertcallback) {
	(function() {
		setTimeout(function() {
			convertCallback = myConvertcallback;
			BMap.Convertor.transMore(points, 2, callback);
		}, 100);
	})();
}

function createMatchMarker(i, obj) {
	var pointstr = $(obj).attr("point").split(",");
	var point = new BMap.Point(pointstr[0], pointstr[1]);
	var match = eval($(obj).attr("match"));
	marker = addMatchMarker(i, point, match);
	$(obj).mouseover(function() {
		markerDo($(this).attr("point"), function(marker) {
			marker.setAnimation(BMAP_ANIMATION_BOUNCE);
			(function() {
				setTimeout(function() {
					marker.setAnimation(null);
				}, 2000);
			})();
		});
	}, function() {
	});
	$(obj).parents(".clickable").click(
			function(event) {
				var link = $(obj);
				var clickingobj = $(event.target);
				if (clickingobj[0].tagName == 'A') {
					//TODO catch click event on link
				} else {
					(function() {
						markerDo(link.attr("point"), function(marker) {
							matchInfo(marker, link.text(), eval(link
									.attr("match")));
						});
					})();
				}
			});
}

function hideOthersInfo(obj, infoid) {
	parent = obj.parents(".panel");
	info = parent.find("#" + infoid);
	$("#matchlist").find(".info:visible").each(function(index, value){
		if (!$(this).is(info))
			$(this).hide();
	});
	return info;
}

function showDetailInfo(obj) {
	infoid = 'detailinfo';
	detailinfo = hideOthersInfo(obj, infoid);
	if (detailinfo.length == 0) {
		var infoobj = jQuery('<div/>', {
			class : 'row display info',
			id : infoid
		});
		match = eval(obj.attr('match'))[0];
		contentTemplate = "<hr>"
			+ "<div class=\"large-6 columns\">"
			+ "<h3>规则:</h3><br/><h4><pre>$rule</pre></h4></div></div>"
            + "<div class=\"large-6 columns\">"
            + "<h3>奖金:</h3><br/><h4><pre>$bonusdetail</h4></pre>"
            + "</div></div>";
		contentTemplate = contentTemplate.replace(/\$rule/g, match.fields.rule)
			.replace(/\$bonusdetail/g, match.fields.bonusdetail);
		infoobj.append(contentTemplate);
		infoobj.appendTo(parent);
		$('html, body').animate({
            scrollTop: obj.offset().top
        }, 2000);
	} else {
		detailinfo.show();
	}
}
function showMoreInfo(obj) {
	infoid = "moreinfo";
	moreinfo = hideOthersInfo(obj, infoid);
	if (moreinfo.length == 0) {
		match = eval(obj.attr('match'));
		url = MOREINFO_URL.replace(/000/g, match[0].fields.poolroom.id);
		$.ajax({
			url : url,
			dataType : 'json',
			success : function(data)
			{
				var infoobj = jQuery('<div/>', {
					class : 'row info',
					id : infoid
				});
				contentTemplate = "<hr>"
					+ "<div class=\"large-8 columns\">"
					+ "<div class=\"orbit-container\">"
					+ "<ul data-orbit style=\"height: 170px\">"
		            + "<li>"
		            + "<img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/orbit/demo1.jpg\">"
		            + "</li>"
		            + "<li class=\"active\">"
		            + "<img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/orbit/demo2.jpg\">"
		            + "</li>"
		            + "</ul></div></div>"
		            + "<div class=\"large-4 columns\">"
		            + "<div class=\"row\">$equipments"
		            + "</div></div>";
				contentEquipment = "";
				for (var idx in data) {
					equipment = data[idx];
		            contentEquipment += "<ul class=\"pricing-table\">"
			            + "<li class=\"title\">" + equipment.fields.tabletype + "</li>"
			            + "<li class=\"price\">" + equipment.fields.price + "元/小时</li>";
		            if (equipment.fields.quantity != 'null')
		            	contentEquipment += "<li class=\"bullet-item\">数量: " + equipment.fields.quantity + "张</li>";
		            if (equipment.fields.producer != 'null')
		            	contentEquipment += "<li class=\"bullet-item\">球桌品牌: " + equipment.fields.producer + "</li>";
		            if (equipment.fields.cue != 'null')
		            	contentEquipment += "<li class=\"bullet-item\">球杆品牌: " + equipment.fields.cue + "</li>";
		            contentEquipment += "</ul>";
				}
				contentTemplate = contentTemplate.replace(/\$equipments/g, contentEquipment);
				infoobj.append(contentTemplate);
				infoobj.appendTo(parent);
				$(document).foundation('orbit');
				$('html, body').animate({
		            scrollTop: obj.offset().top
		        }, 2000);
			}
		});
	} else {
		if ($("#matchlist").find("#moreinfo:visible").length == 0) {
			moreinfo.show();
			$('html, body').animate({
	            scrollTop: obj.offset().top
	        }, 2000);
		} else
			moreinfo.hide();
	}
}

function markerDo(pointstr, callback) {
	var points = pointstr.split(',');
	var point = new BMap.Point(points[0], points[1]);
	var overlays = map.getOverlays();
	for ( var m in overlays) {
		if (overlays[m] instanceof BMap.Marker
				&& overlays[m].getPosition().equals(point)) {
			callback(overlays[m]);
			break;
		}
	}
}

function objectToJsonString(obj) {
	var jsonstring = JSON.stringify(obj);
	return jsonstring.replace(/[\&]/g, '&amp;').replace(/[\<]/g, '&lt;')
			.replace(/[\>]/g, '&gt;').replace(/[\"]/g, '&quot;').replace(
					/[\']/g, '&#39;');
}

function addMatchToList(match, point) {
	var matchobj = jQuery('<div/>', {
		class : 'row',
		id : 'match'
	});
	contentTemplate = "<div class=\"panel radius\">"
			+ "<div class=\"row clickable\">"
			+ "<div class=\"large-8 columns\">"
			+ "<div class=\"row\">"
			+ "<div class=\"large-3 columns\">"
			+ "<a class=\"th\" href=\"#\"><img src=\"http://foundation.zurb.com/docs/v/4.3.2/img/demos/demo1-th.jpg\"></a>"
			+ "</div>"
			+ "<div class=\"large-9 columns\">"
			+ "<h5><span name=\"title\" point=\"$point\" match=\"$matchjsonstr\"><u>$poolroomname</u></span></h5>地图"
			+ "<h6 class=\"subheader\">$address</h6>"
			+ "<h6 class=\"subheader\"><b>报名费</b>: $enrollfee</h6>"
			+ "<h6 class=\"subheader\"><b>报名电话</b>: $enrollfocalpoint</h6>"
			+ "</div></div>"
			+ "<div class=\"row\">"
			+ "<div class=\"large-8 columns\">";
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
	contentTemplate += "</div><div class=\"large-4 columns\"><a href=\"javascript:void(0);\">比赛详情>></a></div>"
			+ "</div></div>"
			+ "<div class=\"large-4 columns\">"
			+ "<div class=\"row display\">"
			+ "<div class=\"large-6 columns\">"
			+ "<div class=\"row\"><div class=\"large-12 columns\"><h2 class=\"subheader\">冠军奖金: <br/><strong>$bonus</strong></h2></div></div>"
			+ "<div class=\"row\"><div class=\"large-12 columns\"><h3>距离: 4.3公里</h3></div></div>"
			+ "</div>"
			+ "<div class=\"large-6 columns\">"
			+ "<div class=\"row\"><div class=\"large-12 columns\"><h3>周赛</h3></div></div>"
			+ "<div class=\"row\"><div class=\"large-12 columns\">"
			+ "<h2>$starttime</h2>"
			+ "</div></div>"
			+ "</div></div>"
			+ "</div>";
	contentTemplate = contentTemplate.replace(/\$point/g,
			point.lng + "," + point.lat).replace(/\$matchjsonstr/g,
			objectToJsonString([ match ])).replace(/\$poolroomname/g,
			match.fields.poolroom.name).replace(/\$starttime/g,
			getFormattedTime2(match.fields.starttime)).replace(/\$bonus/g, match.fields.bonus)
			.replace(/\$address/g, match.fields.poolroom.address).replace(/\$enrollfee/g, match.fields.enrollfee)
			.replace(/\$enrollfocalpoint/g, match.fields.enrollfocal);
	matchobj.append(contentTemplate);
	matchobj.appendTo('#matchlist');
	return matchobj;
}

function createNoMatch() {
	map.centerAndZoom('北京');
	var nomatchobj = jQuery('<div/>', {
		id : 'nomatch',
		class : 'row'
	});
	content = "<div class=\"panel radius\">"
		+ "<div class=\"row\">"
		+ "<h5>您选择的时间段没有比赛。请重新选择。</h5>"
		+ "</div>" + "</div>";
	nomatchobj.append(content);
	nomatchobj.appendTo('#matchlist');
}

function addMatchItems(data) {
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
			for ( var idx in data) {
				matchobj = addMatchToList(data[idx], convertedPoints[idx]);
				createMatchMarker(idx, matchobj.find("span[name=title]"));
			}
		});
	}
}
