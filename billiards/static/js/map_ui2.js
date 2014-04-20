function formatDistance(distance) {
	if (distance < 1000) {
		return Math.floor(distance/100) * 100 + "米";
	} else {
		return Math.round(distance/100)/10 + "公里";
	}
}

var PKLocation = function() {
	var position;

	var consumers = [];

	this.consume = function() {
		if (arguments.length === 0) {
			return;
		}
		if (position) {
			for (var i = 0; i < arguments.length; i++) {
				if (arguments[i] && typeof arguments[i] === 'function') {
					arguments[i](position);
				}
			}
		} else {
			consumers = consumers.concat(Array.prototype.slice.call(arguments, 0));
		}
	};

	var geolocation = new BMap.Geolocation();
	geolocation.getCurrentPosition(function(r){
		if(this.getStatus() === BMAP_STATUS_SUCCESS){
			position = r.point;
			for (var i = 0; i < consumers.length; i++) {
				if (consumers[i] && typeof consumers[i] === 'function') {
					consumers[i](position);
				}
			}
		} else {
        	$("#info .subheader").text("无法获取您当前的位置，请刷新页面重试。");
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

	this.markCurrentLocation = function(myPosition) {
		_this.addMarker(myPosition, STATIC_URL + "images/location.png");
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
				// map.centerAndZoom(myPosition, zoom);
				map.panTo(myPosition);
			}
			map.getContainer().appendChild(div);
			return div;
		};
		map.addControl(control);
	};

	this.addMarker = function(point, iconPath) {
		var icon = new BMap.Icon(iconPath, new BMap.Size(39, 55), {
			anchor : new BMap.Size(15, 53),
			infoWindowAnchor : new BMap.Size(15, 0)
		});
		var marker = new BMap.Marker(point, {
			icon : icon
		});
		map.addOverlay(marker);
		return marker;
	};

	this.removeMarker = function(marker) {
		map.removeOverlay(marker);
	};

	this.setViewport = function(points) {
		map.setViewport(points);
	};
};

var PKPoolrooms = function(pkMap) {
	var markers = [],
		myPosition;

	// 球房模板
	var PoolroomTemplate = '\
		<div class="poolroom panel large-pull-1 large-offset-1 large-3 columns">\
			<div class="pic">\
				{{#image}}\
					<img src="{{path}}" >\
				{{/image}}\
				{{^image}}\
					<img data-caption="MapShot" src="http://api.map.baidu.com/staticimage?center={{point}}&width=104&height=62&zoom=16&scale=2&markers={{point}}&markerStyles=-1">\
				{{/image}}\
			</div>\
			<div>\
				<h5>\
					<span name="title">\
						<a target="_blank" href="{{url}}">{{name}}</a>\
					</span>\
				</h5>\
				<p class="distance">距离我: {{distance}}</p>\
				{{#equip}}\
					<div class="equip icon_list">\
						<span class="ico_none">球房设施: </span>\
						{{#wifi}}\
							<span class="ico_wifi" title="公共区域WIFI"></span>\
						{{/wifi}}\
						{{#freeWifi}}\
							<span class="ico_free_wifi" title="公共区域WIFI"></span>\
						{{/freeWifi}}\
						{{#parking}}\
							<span class="ico_parking" title="停车场"></span>\
						{{/parking}}\
						{{#cafe}}\
							<span class="ico_restaurant" title="餐饮服务"></span>\
						{{/cafe}}\
						{{#subway}}\
							<span class="ico_bus" title="地铁周边"></span>\
						{{/subway}}\
					</div>\
				{{/equip}}\
				<p class="address">地址: {{address}}</p>\
				<p class="tel">电话: {{tel}}</p>\
				<p class="hour">营业时间: {{hour}}</p>\
				{{#coupon}}\
					<div><h5><b>优惠信息</b></h5></div>\
					{{#coupons}}\
						<div><h6><a target="_blank" href="{{url}}">{{title}}</a></h6></div>\
					{{/coupons}}\
				{{/coupon}}\
			</div>\
		</div>\
	';

	// 球房摘要模板
	var PoolroomInfoTemplate = '\
		<div class="mapBubbleInfo"><h6>{{name}}</h6>\
		<p>地址:\
			<strong>{{address}}</strong>\
		</p>\
		<p>营业时间:\
			<strong>{{businessHours}}</strong>\
		</p>\
		{{#distance}}\
			<p>距离我: \
				<strong>{{.}}</strong>\
			</p>\
		{{/distance}}\
	';

	this.loadPoolrooms = function(distance) {
		return function(myPos) {
			if (myPos) {
				myPosition = myPos;
			}
			for (var i = 0; i < markers.length; i++) {
				pkMap.removeMarker(markers[i]);
			}

			createInfo("正在加载附近的球房...");
    		$.ajax({
				url : NEARBY_URL.replace(/00\.00/g, myPosition.lat).replace(/11\.11/g, myPosition.lng)
						.replace(/00/g, distance),
				data : {'f':'json'},
				dataType : 'json',
				success : function(data) {
					if (data.length == 0) {
						$("#info .subheader").text("真遗憾，您附近没有我们收录的球房。");
					} else {
						$("#info").remove();
						layPoolrooms(data);
					}
				},
				error: function (xhr, ajaxOptions, thrownError) {
					$("#info .subheader").text("无法获取周边的球房，请刷新重试。");
				}
			});
		};
	};

	function layPoolrooms(data) {
		var points = [];
		for (var i = 0; i < data.length; i++) {
			var point = new BMap.Point(
				data[i].fields.lng_baidu,
				data[i].fields.lat_baidu
			);
			var poolroomObj = renderPoolroom(data[i], point);
			markers.push(createPoolroomMarker(poolroomObj, data[i], point));
			points.push(point);
		}

		$('#poolrooms .poolroom:nth-child(3n)').after('<br style="clear:both;">');
		if ($('#viewSwitch a.map').hasClass('active')) {
			$('#poolrooms').addClass('large-3 columns').children('.poolroom').removeClass('large-pull-1 large-offset-1 large-3');	
		}

		pkMap.setViewport(points);
	}

	function createPoolroomMarker(obj, poolroom, point) {
		var marker = pkMap.addMarker(point, STATIC_URL + "images/marker.png");
		marker.addEventListener("click", function() {
			poolroomInfo(marker, poolroom);
		});
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

	function renderPoolroom(poolroom, point) {
		var view = {
				"point": point.lng + "," + point.lat,
				"name": poolroom.fields.name,
				"address": poolroom.fields.address,
				"tel": poolroom.fields.tel,
				"hour": poolroom.fields.businesshours,
				"distance": formatDistance(poolroom.fields.distance * 1000),
				"url": POOLROOM_URL.replace(/000/g, poolroom.pk)
			},
			images = Object.getOwnPropertyNames(poolroom.fields.images),
			image,
			coupons = Object.getOwnPropertyNames(poolroom.fields.coupons),
			coupon,
			equip = {},
			i;
		if (images.length !== 0) {
			view["image"] = {};
			for (i in images) {
				image = poolroom.fields.images[images[i]]
				if (image.fields.iscover) {
					view["image"]["path"] = MEDIA_URL + getThumbnail(image.fields.imagepath, '200');
				}
			}
		}

		poolroom.fields.flags.wifi && (equip["wifi"] = true);
		poolroom.fields.flags.freeWifi && (equip["freeWifi"] = true);
		(poolroom.fields.flags.parking || poolroom.fields.flags.parking_free) && (equip["parking"] = true);
		poolroom.fields.flags.cafeteria && (equip["cafe"] = true);
		poolroom.fields.flags.subway && (equip["subway"] = true);
		if (equip.hasOwnProperty()) {
			view["equip"] = equip;
		}

		if (coupons.length > 0) {
			view["coupon"] = {"coupons": []};
			for (i in coupons) {
				coupon = poolroom.fields.coupons[coupons[i]]
				view["coupon"]["coupons"].push({"url": coupon.fields.url}, {"title": coupon.fields.title});
			}
		}

		return $(Mustache.render(PoolroomTemplate, view)).appendTo('#poolrooms');
	}

	function getThumbnail(filename, width) {
		return filename.replace(/(\.[\w\d_-]+)$/i, '-w'+width+'$1');
	}

	
	function poolroomInfo(marker, poolroom) {
		var view = {
			"name": poolroom.fields.name,
			"address": poolroom.fields.address,
			"businessHours": poolroom.fields.businesshours
		};
		if (poolroom.fields.distance) {
			view["distance"] = formatDistance(poolroom.fields.distance * 1000);
		}
		
		var infoWindow = new BMap.InfoWindow(Mustache.render(PoolroomInfoTemplate, view));
		marker.openInfoWindow(infoWindow);
		infoWindow.redraw();
	}
};

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
