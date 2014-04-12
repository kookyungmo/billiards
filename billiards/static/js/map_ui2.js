function formatDistance(distance) {
	if (distance < 1000) {
		return Math.floor(distance/100) * 100 + "米";
	} else {
		return Math.round(distance/100)/10 + "公里";
	}
}
function initialMap(id) {
	var map = new BMap.Map(id);
	map.addControl(new BMap.NavigationControl({anchor: BMAP_ANCHOR_TOP_RIGHT, type: BMAP_NAVIGATION_CONTROL_SMALL}));
    map.enableScrollWheelZoom(true);
    return map;
}
function addMyLocation(point) {
	var marker = addMarker(point, STATIC_URL + "images/location.png");
	marker.setTitle('我的位置');
	return marker;
}

var PKLocation = function() {
	var position;

	var consumers = [];

	this.consume = function(consumer) {
		if (!consumer || typeof consumer !== 'function') {
			return;
		}
		if (position) {
			consumer(position);
		} else {
			console.log(consumer);
			consumers.push(consumer);
		}
	};

	var geolocation = new BMap.Geolocation();
	geolocation.getCurrentPosition(function(r){
		if(this.getStatus() === BMAP_STATUS_SUCCESS){
			position = r.point;
			for (var i in consumers) {
				consumers[i](position);
			}
		} else {
			// 无法获取您当前的位置，请刷新页面重试。
		}
	}, {enableHighAccuracy: false});

};

var PKMap = function(dom, center, zoom) {
	var map = new BMap.Map(dom);
	map.centerAndZoom(center, zoom);
	map.addControl(
		new BMap.NavigationControl({
			anchor: BMAP_ANCHOR_TOP_RIGHT,
			type: BMAP_NAVIGATION_CONTROL_SMALL}
		)
	);
	map.enableScrollWheelZoom(true);

	var _this = this;

	this.markCurrentLocation = function(position) {
		_this.addMarker(position, STATIC_URL + "images/location.png", true);
		// Custom control
		var control = new BMap.Control();
		$.extend(control, {
			defaultAnchor: BMAP_ANCHOR_TOP_LEFT,
			defaultOffset: new BMap.Size(10, 10)
		});
		control.initialize = function() {
			var div = document.createElement("div");
			div.appendChild(document.createTextNode("我的位置"));

			div.style.cursor = "pointer";
			div.style.border = "1px solid gray";
			div.style.backgroundColor = "white";

			div.onclick = function(e){
				// map.centerAndZoom(position, zoom);
				map.panTo(position);
			}
			map.getContainer().appendChild(div);
			return div;
		};
		map.addControl(control);
	};

	var markers = [];

	this.addMarker = function(point, iconPath, durable) {
		var icon = new BMap.Icon(iconPath, new BMap.Size(39, 55), {
			anchor : new BMap.Size(15, 53),
			infoWindowAnchor : new BMap.Size(15, 0)
		});
		var marker = new BMap.Marker(point, {
			icon : icon
		});
		map.addOverlay(marker);
		!durable && markers.push(marker);
	};
};

$.fn.pkMap = function() {
	new PKMap(this[0].id);
	return this;
};

function addCustomToolbar(map, point) {
	var Repan = function() {
		this.defaultAnchor = BMAP_ANCHOR_TOP_LEFT;
		this.defaultOffset = new BMap.Size(10, 10);
	};
	Repan.prototype = new BMap.Control();
	Repan.prototype.initialize = function(map){
		var div = document.createElement("div");
		div.appendChild(document.createTextNode("我的位置"));
	
		div.style.cursor = "pointer";
		div.style.border = "1px solid gray";
		div.style.backgroundColor = "white";
	
		div.onclick = function(e){
			map.centerAndZoom(point, 12);
		}
		map.getContainer().appendChild(div);
		return div;
	}

	map.addControl(new Repan());
}

function addPoolroom(data, mypoint) {	
	points = [];
	if (data.length == 0) {
		map.panTo(mypoint);
	} else
		points.push(mypoint);
	for ( var idx in data) {
		point = new BMap.Point(data[idx].fields.lng_baidu,
				data[idx].fields.lat_baidu);
		poolroomobj = addPoolroomToList(data[idx], point);
		createPoolroomMarker(idx, poolroomobj, data[idx], point);
		points.push(point);
	}
	if (points.length > 0)
		map.setViewport(points);
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
			+ "<ul class=\"clearing-thumbs clearing-feature\" data-clearing>";
	images = Object.getOwnPropertyNames(poolroom.fields.images)
	if (images.length == 0)
		contentTemplate += " <li class=\"clearing-featured-img\"><a class=\"th\" href=\"http://api.map.baidu.com/staticimage?center=$point&width=900&height=600&zoom=18&scale=2&markers=$point&markerStyles=-1,http://billiardsalbum.bcs.duapp.com/2014/01/marker-2.png\"><img data-caption=\"MapShot\" src=\"http://api.map.baidu.com/staticimage?center=$point&width=100&height=62&zoom=16&scale=2&markers=$point&markerStyles=-1\"></a></li>";
	else {
		for (var idx in images) {
			image = poolroom.fields.images[images[idx]]
			contentTemplate += "<li ";
			if ( image.fields.iscover)
				contentTemplate += "class=\"clearing-featured-img\"";
			contentTemplate += "><a href=\"" + MEDIA_URL + image.fields.imagepath 
			+ "\"><img src=\"" + MEDIA_URL + getThumbnail(image.fields.imagepath, '200') + "\"></a></li>";
		}
	}
	contentTemplate += "</ul>"
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
	coupons = Object.getOwnPropertyNames(poolroom.fields.coupons)
	if (coupons.length > 0) {
		contentTemplate += "<div class=\"row\"><h5><b>优惠信息</b></h5></div>";
		for (var i in coupons) {
			coupon = poolroom.fields.coupons[coupons[i]]
			contentTemplate += "<div class=\"row\"><h6><a href=\"" + coupon.fields.url + "\">" + coupon.fields.title + "</a></h6></div>";
		}
	}
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

function getThumbnail(filename, width) {
	return filename.replace(/(\.[\w\d_-]+)$/i, '-w'+width+'$1');
}

var poolroomInfo = function(marker, poolroom) {
	(function() {
		var info = {
			open : function(type, target) {
				var content = "<div class=\"mapBubbleInfo\"><h6>" + poolroom.fields.name + "</h6>";
				content += "<p>地址: <strong>"
					+ poolroom.fields.address
					+ "</strong></p><p>营业时间: <strong>"
					+ poolroom.fields.businesshours
					+ "</strong></p>";
				if (poolroom.fields.distance != null) {
					content += "<p>距离我: <strong>"
						+ formatDistance(poolroom.fields.distance * 1000) + "</strong></p></div>";
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
	var mk = addMarker(point, STATIC_URL + "images/marker.png");
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
