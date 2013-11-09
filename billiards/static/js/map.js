var matchInfo = function(marker, name, matches) {
	(function() {
		var info = {
			open : function(type, target) {
				map.removeEventListener("moveend", info.open);
				map.removeEventListener("tilesloaded", info.open);
				var content = name;
				for ( var idx in matches) {
					content += "<p><p/><strong>奖金: "
							+ matches[idx].fields.bonus
							+ "</strong><br/><strong>比赛时间: "
							+ matches[idx].fields.starttime + "</strong></p>";
				}
				var infoWindow = new BMap.InfoWindow(content);
				marker.openInfoWindow(infoWindow);
				infoWindow.redraw();
			}
		}
		map.addEventListener("moveend", info.open);
		map.addEventListener("tilesloaded", info.open);
	})();
	map.centerAndZoom(marker.getPosition(), 16);
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

function addMatchMarker(i, obj) {
	var points = $(obj).attr("point").split(",");
	var match = eval($(obj).attr("match"));
	point = new BMap.Point(points[0], points[1]);
	var mk = addMarker(point, STATIC_URL + "/images/marker.png");
	mk.addEventListener("click", function() {
		matchInfo(mk, match[0].fields.poolroom.name, match);
	});
}

var convertCallback;
var callback = function(xyResults) {
	var convertedPoints = [];
	var xyResult = null;
	for ( var index in xyResults) {
		xyResult = xyResults[index];
		if (xyResult.error != 0) {
			continue;
		}//TODO
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
	addMatchMarker(i, obj);
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
	$(obj).click(
			function() {
				var link = $(this);
				(function() {
					markerDo(link.attr("point"), function(marker) {
						matchInfo(marker, link.find("strong").text(), eval(link
								.attr("match")));
					});
				})();
			});
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
			+ "<div class=\"row\">"
			+ "<div class=\"large-2 columns\">"
			+ "<a class=\"th\" href=\"#\"><img src=\"http://foundation.zurb.com/docs/img/demos/demo1-th.jpg\"></a>"
			+ "</div>" + "<div class=\"large-6 columns\">"
			+ "<h5><a name=\"match\" point=\"$point\" match=\"$matchjsonstr\">$poolroomname</a><br/>$starttime</h5>"
			+ "<h6 class=\"subheader\">$address</h6>"
			+ "<span class=\"icon_list\">";
	if (match.fields.poolroom.flags.wifi)
		contentTemplate += "<span class=\"ico_wifi\" title=\"公共区域WIFI\"></span>";
	if (match.fields.poolroom.flags.wifi_free)
		contentTemplate += "<span class=\"ico_free_wifi\" title=\"公共区域WIFI\"></span>";
	if (match.fields.poolroom.flags.parking || match.fields.poolroom.flags.parking_free)
		contentTemplate += "<span class=\"ico_parking\" title=\"停车场\"></span>";
	if (match.fields.poolroom.flags.cafeteria)
		contentTemplate += "<span class=\"ico_restaurant\" title=\"餐饮服务\"></span>";
	if (match.fields.poolroom.flags.subway)
		contentTemplate += "<span class=\"ico_bus\" title=\"地铁周边\"></span>";
	contentTemplate += "</span></div>"
			+ "<div class=\"large-4 columns\">" + "<div class=\"row right\">"
			+ "<h4 class=\"subheader\">￥<strong>$bonus</strong></h4>"
			+ "</div>" + "</div>" + "</div>";
	contentTemplate = contentTemplate.replace(/\$point/g,
			point.lng + "," + point.lat).replace(/\$matchjsonstr/g,
			objectToJsonString([ match ])).replace(/\$poolroomname/g,
			match.fields.poolroom.name).replace(/\$starttime/g,
			moment(match.fields.starttime).lang('zh_CN').format('MMMM Do, h:mm a')).replace(/\$bonus/g, match.fields.bonus)
			.replace(/\$address/g, match.fields.poolroom.address);
	matchobj.append(contentTemplate);
	matchobj.appendTo('#matchlist');
	return matchobj;
}

function createNoMatch() {
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
				createMatchMarker(idx, matchobj.find("a[name=match]"));
			}
		});
	}
}