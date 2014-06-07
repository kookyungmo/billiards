function formatDistance(distance) {
	if (distance < 1000) {
		return Math.floor(distance/100) * 100 + "米";
	} else {
		return Math.round(distance/100)/10 + "公里";
	}
}

R=6370996.81;//地球半径
function pi() {
	return Math.PI;
}
function distance(point1, point2) {
	return R*Math.acos(Math.cos(point1.lat*pi()/180 )*Math.cos(point2.lat*pi()/180)*Math.cos(point1.lng*pi()/180 -point2.lng*pi()/180)+
			Math.sin(point1.lat*pi()/180 )*Math.sin(point2.lat*pi()/180))
}

var PKLocation = function(mypos) {
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
	
	if (mypos) {
		position = mypos;
	} else {
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
	}
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
	
	function createIconControl(faClass, clickCallback) {
		var controlIcon = document.createElement("i");
		controlIcon.className = faClass + " fa fa-2 jumbotron-icon";
		controlIcon.style.cursor = "pointer";
		controlIcon.style.border = "1px solid gray";
		controlIcon.onclick = clickCallback;
		return controlIcon;
	}

	this.markCurrentLocation = function(myPosition) {
		_this.myposition = myPosition;
		_this.addMarker(myPosition, STATIC_URL + "images/location.png");
		// Custom control
		var control = new BMap.Control();
		$.extend(control, {
			defaultAnchor: BMAP_ANCHOR_BOTTOM_LEFT,
			defaultOffset: new BMap.Size(isSmall() ? 30: 60, 60)
		});
		control.initialize = function() {			
			var locationIcon = createIconControl("fa-location-arrow", function(e){
				map.panTo(myPosition);
			});
			
			map.getContainer().appendChild(locationIcon);
			return locationIcon;
		};
		map.addControl(control);
	};
	
	this.routeNavigator = function(myposition) {
		// Custom control
		var control = new BMap.Control();
		var heightoffest = $("#pkMap").height() / 15;
		$.extend(control, {
			defaultAnchor: BMAP_ANCHOR_TOP_LEFT,
			defaultOffset: new BMap.Size($("#pkMap").width()/2, heightoffest)
		});
		var prevWidth = $("#pkMap").width();
		$("#pkMap").bind('resize', function(e) {
			control.setOffset(new BMap.Size($("#pkMap").width()/2, heightoffest));
		});
		$("#pkMap").attrchange({
	        callback: function (e) {
	            var curWidth = $(this).width();            
	            if (prevWidth !== curWidth) {
	            	control.setOffset(new BMap.Size($("#pkMap").width()/2, heightoffest));
	            	prevWidth = curWidth;
	            }            
	        }
	    });
		
		var transit = null;
		function addTransitRoute(trasnsitType, BRoute) {
			var transitIcon = createIconControl(trasnsitType, function(e){
				if (_this.myposition) {
					if (transit) {
						if (transit instanceof BRoute)
							return;
						else
							transit.clearResults();
					}
					
					var p1 = _this.myposition;
					var overlays = map.getOverlays();
					for (i in overlays) {
						if (overlays[i] instanceof BMap.Marker) {
							if (!overlays[i].getPosition().equals(p1)) {
								var p2 = overlays[i];
								break;
							}
						}
					}
					options = {map: map, autoViewport: true, panel: 'pkMap-r-result'};						
					if (!isSmall()) {
						$("#pkMap").css("width", "80%");
						$("#pkMap").css("border-right", "2px solid #bcbcbc");
						$("#pkMap-r-result").css("width", "18%");
					} else {
						$("#pkMap-r-result").hide();
						$("#switcher").removeClass("hide");
					}
					
					transit = new BRoute(map, {renderOptions:options});
					targetPoint = {point: p2.getPosition(), title: p2.getTitle(), type: BMap.BMAP_POI_TYPE_NORMAL};
					transit.search(p1, targetPoint);
				}	
			});
			return transitIcon;
		}
		
		control.initialize = function() {
			var div = document.createElement("div");
			div.appendChild(addTransitRoute("fa-car", BMap.DrivingRoute));
			div.appendChild(addTransitRoute("fa-ambulance", BMap.TransitRoute));
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
	
	this.addArchorControl = function(iconClass, marker) {
		var control = new BMap.Control();
		$.extend(control, {
			defaultAnchor: BMAP_ANCHOR_BOTTOM_LEFT,
			defaultOffset: new BMap.Size(isSmall() ? 30: 60, 120)
		});
		control.initialize = function() {			
			var locationIcon = createIconControl(iconClass, function(e){
				map.panTo(marker.getPosition());
			});
			
			map.getContainer().appendChild(locationIcon);
			return locationIcon;
		};
		map.addControl(control);
	};

	this.removeMarker = function(marker) {
		map.removeOverlay(marker);
	};

	this.setViewport = function(points) {
		map.setViewport(points);
	};
	
	this.innerMap = function() {
		return map;
	}
};

var PKPoolrooms = function(pkMap) {
	var markers = [],
		infoWindow,
		myPosition;

	// 球房模板
	var PoolroomTemplate = '\
		<div class="item panel medium-pull-1 medium-offset-1 medium-3 columns">\
			<div class="row collapse">\
				<div class="optional small-5 medium-12 columns">\
						{{#image}}\
							<img src="{{path}}" >\
						{{/image}}\
						{{^image}}\
							<img data-caption="MapShot" src="http://api.map.baidu.com/staticimage?center={{point}}&width=104&height=62&zoom=16&scale=2&markers={{point}}&markerStyles=-1">\
						{{/image}}\
				</div>\
				<div class="small-7 medium-12 columns">\
					<h5>\
						<span name="title">\
							<a target="_blank" href="{{url}}">{{name}}</a>\
						</span>\
					</h5>\
					{{#equip}}\
						<div class="optional icon_list">\
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
					<div class="musthave">地址: {{address}}</div>\
					<div class="optional">营业时间: {{businessHours}}</div>\
					{{#coupon}}\
						<div><h5><b>优惠信息</b></h5></div>\
						{{#coupons}}\
							<div><h5><a target="_blank" href="{{url}}">{{title}}</a></h5></div>\
						{{/coupons}}\
					{{/coupon}}\
				</div>\
			</div>\
			<hr>\
			<div class="row collapse">\
				{{#isSmall}}\
					<div class="small-2 medium-6 columns"><h3><a class="fi-telephone" href="tel://{{tel}}"></a><h3></div>\
				{{/isSmall}}\
				{{^isSmall}}\
					<div class="small-3 medium-6 columns"><a class="fi-telephone" href="tel://{{tel}}">{{tel}}</a></div>\
				{{/isSmall}}\
				<div class="small-4 show-for-small-only columns">\
					<span><a href="{{map_url}}" target="_blank">地图中查看</a></span>\
				</div>\
				<div class="small-6 medium-6 columns">\
					{{#distance}}\
						<span class="musthave" point="{{point}}">距离我: <code>{{distance}}</code></span>\
					{{/distance}}\
					{{^distance}}\
						<span class="musthave hide" point="{{point}}">距离我: <code>{{distance}}</code></span>\
					{{/distance}}\
				</div>\
			</div>\
		</div>\
	';
	
	var PoolroomMessageTemplate = '\
		{{name}} 地址:{{address}} 营业时间:{{businessHours}}\
	';

	// 球房摘要模板
	var PoolroomInfoTemplate = '\
		<div class="mapBubbleInfo"><h6>{{name}}</h6>\
		<p>地址:\
			<code>{{address}}</code>\
		</p>\
		<p>营业时间:\
			<code>{{businessHours}}</code>\
		</p>\
		{{#distance}}\
			<p point="{{point}}">距离我: \
				<code>{{.}}</code>\
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
			var pmarker = createPoolroomMarker(poolroomObj, data[i], point);
			pmarker.setTitle(data[i].fields.name);
			markers.push(pmarker);
			points.push(point);
		}
		
		addPlaceholder(data.length);

		initialViewSwitch();

		pkMap.setViewport(points);
	}

	function createPoolroomMarker(obj, poolroom, point) {
		var marker = pkMap.addMarker(point, STATIC_URL + "images/marker.png");
		marker.addEventListener("click", function() {
			poolroomInfo(marker, poolroom);
		});
		if (obj != null) {
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
		return marker;
	}
	
	function poolroomToView(poolroom) {
		var view = {
				"point": poolroom.fields.lng_baidu + "," + poolroom.fields.lat_baidu,
				"name": poolroom.fields.name,
				"address": poolroom.fields.address,
				"tel": poolroom.fields.tel,
				"distance": "正在获取你的位置",
				"url": POOLROOM_URL.replace(UUID_PATTERN, poolroom.fields.uuid),
				"businessHours": poolroom.fields.businesshours,
				"poolroom_id": poolroom.pk,
				"map_url": PKMAP_URL.replace(/000/g, poolroom.fields.uuid).replace(/mtype/g, "poolroom"),
			},
			images = poolroom.fields.images ? Object.getOwnPropertyNames(poolroom.fields.images) : [],
			image,
			coupons = poolroom.fields.coupons ? Object.getOwnPropertyNames(poolroom.fields.coupons) : [],
			coupon,
			equip = {},
			i;
		if (poolroom.fields.distance) {
			view["distance"] = formatDistance(poolroom.fields.distance * 1000);
		} else if (myPosition) {
			var point = new BMap.Point(poolroom.fields.lng_baidu, poolroom.fields.lat_baidu);
			view["distance"] = formatDistance(distance(myPosition, point));
		}
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
				view["coupon"]["coupons"].push({"url": COUPON_URL.replace(/000/g, coupon.pk), 
					"title": coupon.fields.title});
			}
		}
		if (isSmall()) {
			view["isSmall"] = true;
		}
		return view;
	}
	
	function renderPoolroom(poolroom, point) {
		var view = poolroomToView(poolroom, point);
		return $(Mustache.render(PoolroomTemplate, view)).appendTo('#items');
	}

	function poolroomInfo(marker, poolroom) {
		var poolroomView = poolroomToView(poolroom);
		infoWindow = openInfoWindow(marker, Mustache.render(PoolroomInfoTemplate, poolroomView),
				Mustache.render(PoolroomMessageTemplate, poolroomView));
	}
	
	this.createSinglePoolroomMarker = function(poolroom) {
		point = new BMap.Point(poolroom.fields.lng_baidu,
				poolroom.fields.lat_baidu);
		marker = createPoolroomMarker(null, poolroom, point);
		pkMap.addArchorControl("fa-bookmark", marker);
		setTimeout(function(){
			poolroomInfo(marker, poolroom);
			marker.setAnimation(BMAP_ANIMATION_BOUNCE);
			setTimeout(function(){
				marker.setAnimation(null);
			}, 3000);
		}, 1500);
	};
	
	this.updateDistance = function (myPos) {
		if (myPos)
			myPosition = myPos;
		if (infoWindow && infoWindow.isOpen()) {
			var distanceObj = $(infoWindow.getContent()).find("p[point]");
			var pointstr = distanceObj.attr("point").split(",");
			var point = new BMap.Point(pointstr[0], pointstr[1]);
			if (myPosition)
				distanceObj.children("code").html(formatDistance(distance(myPosition, point)));
			else
				distanceObj.children("code").html("无法获取你的位置");
		}
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

function getThumbnail(filename, width) {
	return filename.replace(/(\.[\w\d_-]+)$/i, '-w'+width+'$1');
}

var PKChallenges = function(pkMap) {
	var markers = [],
		infoWindow,
		myPosition;
	
	var ChallengeTemplate = '\
		<div class="item panel medium-pull-1 medium-offset-1 medium-3 columns">\
			<div class="row collapse">\
				<div class="small-5 medium-12 columns optional">\
					{{#image}}\
						<img src="{{path}}" >\
					{{/image}}\
					{{^image}}\
						<img data-caption="MapShot" src="http://api.map.baidu.com/staticimage?center={{point}}&width=104&height=62&zoom=16&scale=2&markers={{point}}&markerStyles=-1">\
					{{/image}}\
					{{#equip}}\
						<div class="optional icon_list">\
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
				</div>\
				<div class="small-7 medium-12 columns">\
					<p class="musthave">开始时间: <code>{{starttime}}</code></p>\
					<p class="optional">结束时间: <code>{{endtime}}</code></p>\
					<p class="musthave">一名<code>{{level}}</code> <code>{{nickname}}</code>发起在<a target="_blank" href="{{poolroomurl}}">{{name}}</a>的{{type}}</p>\
					<p class="musthave">{{contactway}}: <code>{{contact}}</code></p>\
					<p class="optional">球台类型: <code>{{tabletype}}</code></p>\
				</div>\
			</div>\
			<hr class="optional">\
			<div class="row collapse">\
				<div class="small-4 small-offset-2 show-for-small-only columns">\
					<span><a href="{{map_url}}" target="_blank">地图中查看</a></span>\
				</div>\
				<div class="small-6 medium-12 columns">\
					{{#distance}}\
						<span class="optional" point="{{point}}">距离我: <code>{{distance}}</code></span>\
					{{/distance}}\
					{{^distance}}\
						<span class="optional hide" point="{{point}}">距离我: <code>{{distance}}</code></span>\
					{{/distance}}\
				</div>\
			</div>\
			<div class="row collapse show-for-touch show-for-small-only">\
				<a href="javascript:weixinSendAppMessage(\'{{nickname}}在我为台球狂发起的{{type}}\', \'我为台球狂，一个专注于台球的网站\', \'{{challenge_datail_url}}\', \'{{logo_url}}\');" class="button small secondary fi-share">  发送给好友</a>\
				<a href="javascript:weixinShareTimeline(\'{{nickname}}在我为台球狂发起的{{type}}\', \'我为台球狂，一个专注于台球的网站\', \'{{challenge_datail_url}}\', \'{{logo_url}}\');" class="button small secondary fi-social-picasa">  分享到朋友圈</a>\
			</div>\
		</div>\
	';
	
	var ChallengeMessageTemplate = '\
		{{level}}"{{nickname}}"发起在{{name}}的{{type}}  开始时间:{{starttime}}  结束时间:{{endtime}}\
	';
	
	var ChallengeInfoTemplate = '\
		<div class="mapBubbleInfo">\
		<p>一名<code>{{level}}</code> <code>{{nickname}}</code>发起在<a target="_blank" href="{{poolroomurl}}">{{name}}</a>的{{type}}</p>\
		<p>开始时间:\
			<code>{{starttime}}</code>\
		</p>\
		<p>结束时间:\
		<code>{{endtime}}</code>\
		</p>\
		<p>{{contactway}}: <code>{{contact}}</code></p>\
		<p>球台类型: <code>{{tabletype}}</code></p>\
		{{#distance}}\
			<p point="{{point}}">距离我: \
				<code>{{.}}</code>\
			</p>\
		{{/distance}}\
	';
	
	this.loadChallenges = function(mypos) {
		for (var i = 0; i < markers.length; i++) {
			pkMap.removeMarker(markers[i]);
		}

		createInfo("正在加载约球信息...");
		url = CHALLENGE_URL;
		if (mypos) {
			url = CHALLENGE_WITH_DISTANCE_URL;
			url = url.replace(/00\.00/g, myPosition.lat).replace(/11\.11/g, myPosition.lng);
		}
		$.ajax({
			url : url,
			data : {'f':'json'},
			dataType : 'json',
			success : function(data)
			{
				if (data.length == 0) {
					createInfo("真遗憾，暂时没有球友和俱乐部发布的约球信息。");
				} else {
					$("#info").remove();
					layChallenges(data);
					$(document).foundation({
				    	abide: abideOptions
				    });
				}
			},
			error: function (xhr, ajaxOptions, thrownError) {
				createInfo("无法获取约球信息，请刷新重试。");
		     }
		});
	};
	
	this.layChallenge = function(data) {
		layChallenges(data);
		switchToMap();
		setTimeout(function(){
			challengeInfo(markers[0], data[0], markers[0].getPosition());
			markers[0].setAnimation(BMAP_ANIMATION_BOUNCE);
			setTimeout(function(){
				markers[0].setAnimation(null);
			}, 3000);
		}, 1500);
	};
	
	this.updateDistance = function(myPos) {
		if (myPos) {
			myPosition = myPos;
			$(".item span[point]").each(function() {
				var pointstr = $(this).attr("point").split(",");
				var point = new BMap.Point(pointstr[0], pointstr[1]);
				$(this).children("code").html(formatDistance(distance(myPosition, point)));
				$(this).removeClass("hide");
			});
		} else {
			$(".item span[point] code").each(function() {
				$(this).html("无法获取你的位置");
			})
		}
		if (infoWindow && infoWindow.isOpen()) {
			var distanceObj = $(infoWindow.getContent()).find("span[point]");
			var pointstr = distanceObj.attr("point").split(",");
			var point = new BMap.Point(pointstr[0], pointstr[1]);
			if (myPosition)
				distanceObj.children("code").html(formatDistance(distance(myPosition, point)));
			else
				distanceObj.children("code").html("无法获取你的位置");
		}
	}
		
	function layChallenges(data) {
		var points = [];
		for (var i = 0; i < data.length; i++) {
			var point = new BMap.Point(
				data[i].fields.lng_baidu,
				data[i].fields.lat_baidu
			);
			var challengeObj = renderChallenge(data[i], point);
			markers.push(createChallengeMarker(challengeObj, data[i], point));
			points.push(point);
		}
		
		addPlaceholder(data.length);

		initialViewSwitch();

		pkMap.setViewport(points);
	}
	
	function challengeToView(challenge, point) {
		var view = {
				"point": point.lng + "," + point.lat,
				"name": challenge.fields.poolroom.name,
				"poolroomurl": POOLROOM_URL.replace(UUID_PATTERN, challenge.fields.poolroom.uuid),
				"starttime": getSmartTime(challenge.fields.starttime),
				"endtime": getSmartTime(challenge.fields.expiretime),
				"level": challenge.fields.level,
				"nickname": challenge.fields.issuer_nickname == null ? "" : challenge.fields.issuer_nickname,
				"type": challenge.fields.source == 1 ? "约赛" : "抢台费",
				"tabletype": challenge.fields.tabletype,
				"challenge_datail_url": CHALLENGE_DETAIL_URL.replace(/000/g, challenge.pk),
				"logo_url": LOGO_URL,
				"challenge_id": challenge.pk,
				"map_url": PKMAP_URL.replace(/000/g, challenge.pk).replace(/mtype/g, "challenge"),
			},
			images = Object.getOwnPropertyNames(challenge.fields.poolroom.images),
			image,
			equip = {},
			i;
		if (images.length !== 0) {
			view["image"] = {};
			for (i in images) {
				image = challenge.fields.poolroom.images[images[i]]
				if (image.iscover) {
					view["image"]["path"] = MEDIA_URL + getThumbnail(image.imagepath, '200');
				}
			}
		}
		challenge.fields.poolroom.flags.wifi && (equip["wifi"] = true);
		challenge.fields.poolroom.flags.freeWifi && (equip["freeWifi"] = true);
		(challenge.fields.poolroom.flags.parking || challenge.fields.poolroom.flags.parking_free) && (equip["parking"] = true);
		challenge.fields.poolroom.flags.cafeteria && (equip["cafe"] = true);
		challenge.fields.poolroom.flags.subway && (equip["subway"] = true);
		if (equip.hasOwnProperty()) {
			view["equip"] = equip;
		}
		
		if (myPosition)
			view["distance"] = formatDistance(distance(myPosition, point));

		var protocols = [["tel://", "电话"], ["qq://", "QQ"], ["wechat://", "微信"]];
		for (idx in protocols) {
			protocol = protocols[idx];
			if (challenge.fields.issuer_contact.indexOf(protocol[0]) == 0) {
				method = protocol[1];
				contactinfo = challenge.fields.issuer_contact.substring(protocol[0].length);
				break;
			}
		}
		if (method == undefined) {
			method = "联系方式";
			contactinfo = challenge.fields.issuer_contact;
		}
		view["contactway"] = method;
		view["contact"] = contactinfo;
		if (challenge.fields.source == 2 && challenge.fields.location != '') {
			view["name"] = "地图位置";
			view["poolroomurl"] = "javascript:void(0);";
			locationdata = challenge.fields.location.split(":");
			if (locationdata.length > 1)
				view["name"] = locationdata[1];
		}
		return view;
	}
	
	function renderChallenge(challenge, point) {
		var view = challengeToView(challenge, point);
		
		if (challenge.fields.source == 1) {
			//TODO add challege apply
		}

		return $(Mustache.render(ChallengeTemplate, view)).appendTo('#items');
	}	
	
	this.addChllengeMarker = function(challenge) {
		var point = new BMap.Point(
				challenge.fields.lng_baidu,
				challenge.fields.lat_baidu
			);
		var marker = createChallengeMarker(null, challenge, point);
		challengeInfo(marker, challenge, point);
	};
	
	function createChallengeMarker(obj, challenge, point) {
		var marker = pkMap.addMarker(point, STATIC_URL + "images/marker.png");
		marker.addEventListener("click", function() {
			challengeInfo(marker, challenge, point);
		});
		if (obj != null) {
			(function(){
				$(obj).click(
					function(event) {
						var link = $(obj);
						var clickingobj = $(event.target);
						if (clickingobj[0].tagName == 'A') {
							//TODO catch click event on link
						} else {
							challengeInfo(marker, challenge, point);
						}
					});
			})();
		}
		return marker;
	}
	
	function challengeInfo(marker, challenge, point) {
		var view = challengeToView(challenge, point);
		view["distance"] = myPosition ? formatDistance(distance(myPosition, point)) : "正在获取你的位置";
		infoWindow = openInfoWindow(marker, Mustache.render(ChallengeInfoTemplate, view),
				Mustache.render(ChallengeMessageTemplate, view));
	}
}

function openInfoWindow(marker, innerHtml, message) {
	var infoOptions = {
		"message": message,	
	};
	if (isSmall()) {
		infoOptions["height"] = 200;
		infoOptions["width"] = 100;
	}
	marker.getMap().panTo(marker.getPosition());
	var infoWindow = new BMap.InfoWindow(innerHtml, infoOptions);
	infoWindow.enableAutoPan();
	marker.openInfoWindow(infoWindow);
	infoWindow.redraw();
	return infoWindow;
}

var PKMatches = function(pkMap) {
	var markers = [],
		myPosition, infoWindow;
	
	var CalendarTemplate = '\
		{{#monthes}}\
			<dl class="sub-nav">\
				<dt><strong>{{month}}</strong></dt>\
				{{#days}}\
				<dd class="{{active}}"><a class="{{money}}" timestamp="{{timestamp}}" href="javascript:void(0);">{{day}}</a></dd>\
				{{/days}}\
			</dl>\
		{{/monthes}}\
	';
	
	var MatchTemplate = '\
		<div class="item panel medium-pull-1 medium-offset-1 medium-3 columns">\
			<div class="row collapse">\
				<div class="optional small-5 medium-12 columns">\
					{{#image}}\
						<img src="{{path}}" >\
					{{/image}}\
					{{^image}}\
						<img data-caption="MapShot" src="http://api.map.baidu.com/staticimage?center={{point}}&width=104&height=62&zoom=16&scale=2&markers={{point}}&markerStyles=-1">\
					{{/image}}\
				</div>\
				<div class="small-7 medium-12 columns">\
					<p class="musthave"><a href="{{match_detail_url}}">{{title}}</a></p>\
					<p class="musthave">{{type}}球馆: <a href="{{poolroom_url}}">{{poolroom_name}}</a>\
					<p class="{{addressAttr}}">球馆地址: {{poolroom_address}}\
					{{#equip}}\
						<div class="optional icon_list">\
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
					<p class="musthave">开始时间: <code>{{starttime}}</code></p>\
					{{#hasPrize}}\
					<p class="optional {{prizeAttr}}">冠军奖励: <code>\
					{{#bonus}}\
					现金: {{bonus}}元\
					{{/bonus}}\
					{{#rechargeablecard}}\
					俱乐部充值卡: {{rechargeablecard}}元\
					{{/rechargeablecard}}\
					{{#otherprize}}\
					{{otherprize}}\
					{{/otherprize}}\
					</code></p>\
					{{/hasPrize}}\
					<p class="optional {{enroolFeeAttr}}">报名费: <code>{{enroll_fee}}</code></p>\
					{{#enroll_focal}}\
					{{/enroll_focal}}\
				</div>\
			</div>\
			<div class="row collapse">\
				<div class="small-3 small-offset-2 show-for-small-only columns">\
					<span><a href="{{map_url}}" target="_blank">地图中查看</a></span>\
				</div>\
				<div class="small-6 medium-12 columns">\
					{{#distance}}\
						<span class="optional" point="{{point}}">距离我: <code>{{distance}}</code></span>\
					{{/distance}}\
					{{^distance}}\
						<span class="optional hide" point="{{point}}">距离我: <code>{{distance}}</code></span>\
					{{/distance}}\
				</div>\
			</div>\
		</div>\
	';
	
	var MatchInfoMessage = '\
		{{title}} {{starttime}}在{{poolroom_name}}({{poolroom_address}})\
	';
	
	var MatchInfoTemplate = '\
		<div class="mapBubbleInfo row collapse">\
			<div class="small-5 columns">\
				{{#image}}\
					<img src="{{path}}" >\
				{{/image}}\
				{{^image}}\
					<img data-caption="MapShot" src="http://api.map.baidu.com/staticimage?center={{point}}&width=104&height=62&zoom=16&scale=2&markers={{point}}&markerStyles=-1">\
				{{/image}}\
			</div>\
			<div class="small-7 columns">\
				<h6>{{name}}</h6>\
				<a href="{{match_detail_url}}" onclick="javascript:clickLinkInInfo(this);">{{title}}</a>\
				{{#distance}}\
				<p point="{{point}}">距离我: <code>{{distance}}</code></p>\
				{{/distance}}\
				<p>{{type}}球馆: <a href="{{poolroom_url}}" onclick="javascript:clickLinkInInfo(this);">{{poolroom_name}}</a></p>\
				<p class="{{insideAttr}}">球馆地址: {{poolroom_address}}</p>\
				{{#equip}}\
				<div class="optional icon_list {{insideAttr}}">\
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
				<p class="{{insideAttr}}">开始时间: <code>{{starttime}}</code></p>\
				{{#hasPrize}}\
				<p>冠军奖励: <code>\
				{{#bonus}}\
				现金: {{bonus}}元\
				{{/bonus}}\
				{{#rechargeablecard}}\
				俱乐部充值卡: {{rechargeablecard}}元\
				{{/rechargeablecard}}\
				{{#otherprize}}\
				{{otherprize}}\
				{{/otherprize}}\
				</code></p>\
				{{/hasPrize}}\
			</div>\
		</div>\
	';
	
	var MATCH_MARKER_URL = STATIC_URL + "images/marker.png";
	var PrizeAttr = "";
	var AddressAttr = "hide";
	var EnroolFeeAttr = "";
	var DefaultMapInsideVisible = "hide";
	var ITEM_PARENT_ELEMENT = "#items";
	
	this.buildCalendar = function(starttime, endtime, bonusobj, summary, intervals) {
		var bonussummary = {};
		for (var idx in bonusobj) {
			bonussummary[bonusobj[idx].starttime] = bonusobj[idx].bonus;
		}
		
		var m = starttime.clone();
		var selectedTimestamp = getParameterByName('s');
		if (selectedTimestamp != null) {
			var initialDay = moment.unix(selectedTimestamp);
			if (!(initialDay.unix() >= starttime.unix() && initialDay.unix() <= endtime.unix()))
				initialDay = null;
		}
		var thismonth = m.month();
		view = {
			"monthes": [
			    {"month": m.lang('zh_CN').format('MMM')},
			]
		};
		var days = [];
		for (var i = 0; i < intervals; i++) {
			if (m.month() != thismonth) {
				view["monthes"][view["monthes"].length - 1]["days"] = days;
				days = [];
				thismonth = m.month();
				view["monthes"].push({"month": m.lang('zh_CN').format('MMM')});
			}
			var day = {
				"day": m.format('DD') + " " + m.format('dddd'),
				"timestamp": m.unix(),
			};
			if (initialDay != null) {
				if (m.date() == initialDay.date() && m.month() == initialDay.month())
					day["active"] = "active";
			} else if (m.date() == starttime.date() && m.month() == starttime.month())
				day["active"] = "active";
			var formattedday = m.format("YYYY-MM-DD");
			if (formattedday in summary) {
				day["day"] += "(" + summary[formattedday] + ")";
			}
			if (formattedday in bonussummary) {
				day["money"] = "fi-trophy";
			}
			m.add('days', 1);
			days.push(day);
		}
		view["monthes"][view["monthes"].length - 1]["days"] = days;
		
		return $(Mustache.render(CalendarTemplate, view)).appendTo('#calendarSelect');
	};
	
	this.loadRedbullMatches = function() {
		MATCH_MARKER_URL = "http://bcs.duapp.com/billiardsalbum/2014/05/redbull-marker-256.gif";
		PrizeAttr = "optional";
		AddressAttr = "musthave";
		if (isSmall()) {
			EnroolFeeAttr = "hide";
			AddressAttr = "hide";
		} else {
			ITEM_PARENT_ELEMENT = '.cbp_tmtimeline';
			jQuery('<ul/>', {
			    class: 'cbp_tmtimeline'
			}).appendTo('#items');
			MatchTemplate = '\
				<li>\
					<time class="cbp_tmtime" datetime="2013-04-10"><span>{{matchdate}}</span></time>\
					<div class="cbp_tmicon"></div>\
					<div class="cbp_tmlabel">\
						<p class="musthave"><a href="{{match_detail_url}}">{{title}}</a></p>\
						<p class="musthave">{{type}}球馆: <a href="{{poolroom_url}}">{{poolroom_name}}</a>\
						<p class="musthave">开始时间: <code>{{matchtime}}</code></p>\
					</div>\
				</li>';
		}
		createInfo("正在加载红牛比赛及球房...");
		$.ajax({
			url : REDBULL_URL,
			data : {'f':'json'},
			dataType : 'json',
			success : function(data) {
				if (data.length == 0) {
					$("#info .subheader").text("真遗憾，还没有比赛被收录。");
				} else {
					$("#info").remove();
					for (var idx = 0; idx < data.length; idx++) {
						var image = {
							imagepath: "/2014%2F05%2Fredbull-activity.jpg",
							iscover: true,
							description: '',
						};
						var images = Object.getOwnPropertyNames(data[idx].fields.poolroom.images);
						var newimages = {};
						if (images.length !== 0) {
							newimages["img" + images.length] = image;
							for (i in images) {
								newimages[images[i]] = data[idx].fields.poolroom.images[images[i]];
							}
						} else {
							newimages["img0"] = image;
						}
						data[idx].fields.poolroom.images = newimages;
					}
					layMatches(data);
					if (!isSmall())
						switchToMap();
				}
			},
			error: function (xhr, ajaxOptions, thrownError) {
				$("#info .subheader").text("无法获取比赛和球房，请刷新重试。");
			}
		});
	};
	
	this.layMatches = layMatches;
	
	this.loadMatches = function(timestamp) {
		createInfo("正在加载选定日期的比赛和活动...");

		for (var i = 0; i < markers.length; i++) {
			pkMap.removeMarker(markers[i]);
		}
		
		selecteddate = moment.utc(timestamp);
		$.ajax({
			url : MATCH_URL,
			data : {'f':'json', 'starttime':timestamp, 'endtime': selecteddate.add('days', 1).unix()},
			dataType : 'json',
			success : function(data)
			{
				newloc = setGetParameter(window.location.pathname, 's', timestamp);
				window.history.pushState({ path: newloc }, '', newloc);
				if (data.length == 0) {
					createInfo("你选择的日期没有比赛和活动被收录，请选择别的日期。");
				} else {
					$("#info").remove();
					layMatches(data);
				}
			},
			error: function (xhr, ajaxOptions, thrownError) {
				createInfo("无法获取比赛活动信息，请刷新重试。");
			}
		});
	};
	
	this.updateDistance = function(myPos) {
		if (myPos) {
			myPosition = myPos;
			$(".item span[point]").each(function() {
				var pointstr = $(this).attr("point").split(",");
				var point = new BMap.Point(pointstr[0], pointstr[1]);
				$(this).children("code").html(formatDistance(distance(myPosition, point)));
				$(this).removeClass("hide");
			});
		} else {
			$(".item span[point] code").each(function() {
				$(this).html("无法获取你的位置");
			})
		}
		if (infoWindow && infoWindow.isOpen()) {
			var distanceObj = $(infoWindow.getContent()).find("span[point]");
			if (distanceObj.length) {
				var pointstr = distanceObj.attr("point").split(",");
				var point = new BMap.Point(pointstr[0], pointstr[1]);
				if (myPosition)
					distanceObj.children("code").html(formatDistance(distance(myPosition, point)));
				else
					distanceObj.children("code").html("无法获取你的位置");
			}
		}
	};
	
	function layMatches(data) {
		var points = [];
		for (var i = 0; i < data.length; i++) {
			var point = new BMap.Point(
				data[i].fields.poolroom.lng,
				data[i].fields.poolroom.lat
			);
			var matchObj = renderMatch(data[i], point);
			markers.push(createMatchMarker(matchObj, data[i], point));
			points.push(point);
		}
		
		addPlaceholder(data.length);

		initialViewSwitch();

		pkMap.setViewport(points);
	}
	
	this.addMatchMarker = function(match) {
		var point = new BMap.Point(
				match.fields.poolroom.lng,
				match.fields.poolroom.lat
			);
		var marker = createMatchMarker(null, match, point);
		pkMap.addArchorControl("fa-bookmark", marker);
		setTimeout(function(){
			matchInfo(marker, match, point);
			marker.setAnimation(BMAP_ANIMATION_BOUNCE);
			setTimeout(function(){
				marker.setAnimation(null);
			}, 3000);
		}, 1500);
	}
	
	function createMatchMarker(obj, match, point) {
		var marker = pkMap.addMarker(point, MATCH_MARKER_URL);
		marker.setTitle(match.fields.title + "(" + match.fields.poolroom.name + ")");
		marker.addEventListener("click", function() {
			matchInfo(marker, match, point);
		});
		if (obj != null) {
			(function(){
				$(obj).click(
					function(event) {
						var link = $(obj);
						var clickingobj = $(event.target);
						if (clickingobj[0].tagName == 'A') {
							//TODO catch click event on link
						} else {
							matchInfo(marker, match, point);
						}
					});
			})();
		}
		return marker;
	}
	
	function matchInfo(marker, match, point) {
		var matchView = matchToView(match, point);
		infoWindow = openInfoWindow(marker, Mustache.render(MatchInfoTemplate, matchView),
				Mustache.render(MatchInfoMessage, matchView));
	}
	
	function matchToView(match, point) {
		var view = {
				"match_id": match.pk,
				"point": point.lng + "," + point.lat,
				"poolroom_name": match.fields.poolroom.name,
				"poolroom_url": POOLROOM_URL.replace(UUID_PATTERN, match.fields.poolroom.uuid),
				"poolroom_address": match.fields.poolroom.address,
				"starttime": getSmartTime(match.fields.starttime),
				"title": match.fields.title,
				"enroll_fee": match.fields.enrollfee,
				"enroll_focal": match.fields.enrollfocal,
				"prizeAttr": PrizeAttr,
				"addressAttr": AddressAttr,
				"enroolFeeAttr": EnroolFeeAttr,
				"map_url": PKMAP_URL.replace(/000/g, match.pk).replace(/mtype/g, "match"),
				"insideAttr": DefaultMapInsideVisible,
				"matchdate": getFormattedTime(match.fields.starttime),
				"matchtime": getFormattedTime2(match.fields.starttime),
			},
			images = Object.getOwnPropertyNames(match.fields.poolroom.images),
			image,
			equip = {},
			i;
		if (images.length !== 0) {
			view["image"] = {};
			for (i in images) {
				image = match.fields.poolroom.images[images[i]];
				view["image"]["path"] = MEDIA_URL + getThumbnail(image.imagepath, '200');
				if (image.iscover) {
					view["image"]["path"] = MEDIA_URL + getThumbnail(image.imagepath, '200');
					break;
				}
			}
		}

		match.fields.poolroom.flags.wifi && (equip["wifi"] = true);
		match.fields.poolroom.flags.freeWifi && (equip["freeWifi"] = true);
		(match.fields.poolroom.flags.parking || match.fields.poolroom.flags.parking_free) && (equip["parking"] = true);
		match.fields.poolroom.flags.cafeteria && (equip["cafe"] = true);
		match.fields.poolroom.flags.subway && (equip["subway"] = true);
		if (equip.hasOwnProperty()) {
			view["equip"] = equip;
		}
		
		if (myPosition)
			view["distance"] = formatDistance(distance(myPosition, point));
			
		if (match.fields.type == 1) {
			view["match_detail_url"] = MATCH_DETAIL_URL.replace(/000/g, match.pk);
			view["hasPrize"] = true;
			if (match.fields.bonus > 0)
				view["bonus"] = match.fields.bonus;
			if (match.fields.rechargeablecard > 0)
				view["rechargeablecard"] = match.fields.rechargeablecard;
			if (match.fields.otherprize != null)
				view["otherprize"] = match.fields.otherprize;
		}
		else 
			view["match_detail_url"] = ACTIVITY_URL.replace(/000/g, match.pk);

		return view;
	}
	
	function renderMatch(match, point) {
		var view = matchToView(match, point);
		return $(Mustache.render(MatchTemplate, view)).appendTo(ITEM_PARENT_ELEMENT);
	}
}

function initialViewSwitch() {
	$('#items .item:nth-child(3n)').after('<br style="clear:both;">');
	if ($('#viewSwitch a.map').hasClass('active')) {
		$('#items').addClass('map medium-3 columns').children('.item').removeClass('medium-pull-1 medium-offset-1 medium-3');
		$('#content').addClass('map medium-3 columns');
	}
}

function switchToMap() {
	$('#items').addClass('map medium-3 columns').children('.item').removeClass('medium-pull-1 medium-offset-1 medium-3');	
	$('#content').addClass('map medium-3 columns');
	$('#mapContainer').removeClass('hidden');
}

function switchToList() {
	$('#mapContainer').addClass('hidden');
	$('#items').removeClass('map medium-3 columns').children('.item').addClass('medium-pull-1 medium-offset-1 medium-3');
	$('#content').removeClass('map medium-3 columns');
}

function setUpViewSwitch() {
	$('#viewSwitch a').click(function() {
		if ($(this).hasClass('active')) {
			return false;
		}
		if ($(this).hasClass('list')) {
			switchToList();
		} else if ($(this).hasClass('map')) {
			switchToMap();
		}

		$(this).addClass('active').siblings().removeClass('active');
		return false;
	});
	
	$(window).scroll(function() {
		if ($('#items').height() <= $('#pkMap').height()) {
			return;
		}
		if ($(window).scrollTop() > $('#mapContainer').offset().top) {
			$('#pkMap').css({
				'position': 'fixed',
				'top': 0,
				'width': $('#mapContainer').width()
			});
		} else {
			$('#pkMap').css({
				'position': 'relative'
			});
		}
	});
}

function addPlaceholder(length) {
	if (length % 3 == 2) {
		var emptyobj = jQuery('<div/>', {
			class : 'medium-pull-1 medium-offset-1 medium-3 columns',
		});
		emptyobj.appendTo('#items');
	}
}

function clickLinkInInfo(link) {
	if (inIframe()) {
		window.top.location = $(link).attr('href');
		return false;
	}
}
