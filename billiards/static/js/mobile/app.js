var MobileDevice = {
    Android: function() {
        return navigator.userAgent.match(/Android/i);
    },
    BlackBerry: function() {
        return navigator.userAgent.match(/BlackBerry/i);
    },
    iOS: function() {
        return navigator.userAgent.match(/iPhone|iPad|iPod/i);
    },
    Opera: function() {
        return navigator.userAgent.match(/Opera Mini/i);
    },
    Windows: function() {
        return navigator.userAgent.match(/IEMobile/i);
    },
    any: function() {
        return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
    }
};

function mapURI(lat, lng) {
	if (MobileDevice.iOS()) {
		return "http://maps.apple.com/?q=" + lat + "," + lng;
	} else if (MobileDevice.Windows()){
		return "maps:" + lat + "," + lng;
	} else
		return "geo:" + lat + "," + lng;
}

function isWechat() {
	var ua = navigator.userAgent.toLowerCase();
    if(ua.match(/MicroMessenger/i)=="micromessenger") {
        return true;
    } else {
        return false;
    }
}

function setGetParameter(url, paramName, paramValue)
{
	paramValue = encodeURIComponent(paramValue);
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName));
        var suffix = url.substring(url.indexOf(paramName)).substring(url.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
    if (url.indexOf("?") < 0)
        url += "?" + paramName + "=" + paramValue;
    else
        url += "&" + paramName + "=" + paramValue;
    }
    return url;
}

function dologin(url) {
	dologin2(url, window.location.pathname + window.location.search);
}

function dologin2(url, returnurl) {
	window.location.href = setGetParameter(url, 'returnurl', returnurl);
}

function refreshAuthentication() {
	if (isWechat())
		dologin('/user/login/wechat');
	else
		window.location.href = setGetParameter('/user/login', 'from', 
				window.location.pathname + window.location.search + window.location.hash);
}

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

var currentPosition = null;
function fetchBMapLocation(callback) {
	if (currentPosition)
		callback(currentPosition);
	else
		new BMap.Geolocation().getCurrentPosition(function(r){
			if(this.getStatus() === BMAP_STATUS_SUCCESS){
				currentPosition = r.point;
				callback(currentPosition);
			}
		}, {enableHighAccuracy: false});
}

if(!Object.keys) Object.keys = function(o){
    if (o !== Object(o))
         throw new TypeError('Object.keys called on non-object');
    var ret=[],p;
    for(p in o) if(Object.prototype.hasOwnProperty.call(o,p)) ret.push(p);
    return ret;
}

moment.locale("zh-CN");

function calcDistance(mypoint, locations) {
	var max = min = 0;
	for (var i = 0; i < locations.length; i++) {
		var dist = distance(mypoint, locations[i]);
		if (min == 0 || min > dist)
			min = dist;
		if (max == 0 || max < dist)
			max = dist;
	}
	if (min == max)
		offerdistance = formatDistance(min);
	else
		offerdistance = formatDistance(min) + "-" + formatDistance(max);
	return {'min': min, 'max': max, 'distanceLabel': offerdistance};
}

function parseTime(timestr) {
	return moment(timestr, moment.ISO_8601).zone('+0800');
}

var ORDER_URL = "/transaction/goods/12345678901234567890123456789012";

var staticurl = 'static/m/';
angular.module('app',['ngRoute','hmTouchEvents','infinite-scroll'])
.service('scopeService', function() {
     return {
         safeApply: function ($scope, fn) {
             var phase = $scope.$root.$$phase;
             if (phase == '$apply' || phase == '$digest') {
                 if (fn && typeof fn === 'function') {
                     fn();
                 }
             } else {
                 $scope.$apply(fn);
             }
         },
     };
})
.service('offerService', function(){
	var dayRange = _.range(3);
	var buffer = 2;
	
	
	function setTime(timestr, time) {
		var timearray = timestr.split(":");
		time.hour(timearray[0]);
		time.minute(0);
		return time;
	}
	
	this.offerPriceLocation = function(offers) {
		var maxprice = minprice = 0;
		var poolrooms = [];
		var locations = [];
		for (var i in dayRange) {
			for (var j = 0; j < offers[i].length; j++) {
				if (minprice == 0 || minprice > offers[i][j].price)
					minprice = offers[i][j].price;
				if (maxprice == 0 || maxprice < offers[i][j].price)
					maxprice = offers[i][j].price;
				if ($.inArray(offers[i][j].poolroom.name, poolrooms) == -1) {
					poolrooms.push(offers[i][j].poolroom);
					locations.push(new BMap.Point(
						offers[i][j].poolroom.lng, offers[i][j].poolroom.lat
					));
				}
			}
		}
		if (maxprice != minprice)
			offerprice = minprice + "-" + maxprice;
		else
			offerprice = minprice;
		
		return {'offerprice': offerprice, 'locations': locations, 'poolrooms': poolrooms, 'minprice': minprice,
			'maxprice': maxprice};
	}
	
	this.poolroomsDisplay = function(poolrooms) {
		var pnames = [];
		var pobj = {};
		for (var idx in poolrooms) {
			if (pobj[poolrooms[idx].name])
				continue;
			pobj[poolrooms[idx].name] = true;
			pnames.push(poolrooms[idx].name);
		}
		var pdisplay = '';
		if (pnames.length > 0)
			pdisplay = pnames.join("/");
		else
			pdisplay = pnames[0];
		return pdisplay;
	}
	
	this.latestOffer = function(offers){
		var now = moment().startOf("hour").add(1, 'h');
		var end = moment();
		var start = now.clone().add(buffer, 'h');
		for (var i in dayRange) {
			var min_start = null;
			var diffdays = moment().clone().startOf("day").diff(end.clone().startOf("day"), 'd');
			var inRange = false;
			for (var j = 0; j < offers[i].length; j++) {
				if (min_start == null)
					min_start = setTime(offers[i][j].starttime, end.clone());
				else if (min_start.diff(setTime(offers[i][j].starttime, end.clone())) > 0)
					min_start = setTime(offers[i][j].starttime, end.clone());
				if (start.diff(setTime(offers[i][j].endtime, end.clone())) < 0)
					inRange = true;
			}
			
			if (diffdays == 0) {
				if (start.diff(min_start) < 0)
					return min_start;
				else if (inRange)
					return start;
			} else if (min_start != null)
				return min_start;
			
			end.add(1, 'd');
		}
		return null;
	}
	
	this.formatLatestOffer = function(start) {
		return start === null ? "" : start.calendar();
	}
	
	this.offerDays = function(offers) {
		var offerdays = [];
		var starthour = moment().startOf("hour").add(buffer + 1, 'h');
		for (var i in dayRange) {
			var day = moment().startOf('day');
			day.add(i, 'd');
			hours = [];
			for (var j = 0; j < offers[i].length; j++) {
				var start, end;
				if (starthour.clone().startOf('day').diff(day, 'd') <= 0) {
					var start2 = setTime(offers[i][j].starttime, day.clone());
					start = starthour.diff(start2) > 0 ? starthour.clone() : start2;
					end = setTime(offers[i][j].endtime, day.clone());
				} else {
					continue;
				}
				if (end.diff(start, 'h') > 0) {
					hours = hours.concat(_.range(start.hour(), end.hour()));
				}
			}
			if (hours.length > 0) {
				offerdays.push({'hours': hours, 'day': day, 'offer': offers[i], 'idx': i});
			}
		}
		return offerdays;
	}
})
.factory('Data',function($http, offerService){

	var Data = function(id, actor){
		this.actor = actor;
		
		this.id = id;

		// 导航数据
		this.navData = [];

		// 翻页
		this.busy = false;
	    this.after = 1;
	    this.complete = false;

		// 列表页数据 list data
		this.listData = [];
        
        // 详细页数据 detail data
	    this.person = [];
	    this.offers = [];

	    // 预约数据
        this.bookDate = [];
        this.bookTime = [];
        this.bookDuration = [];

        // 订单数据
        this.orderData = [];
        this.orderDtailData = [];

	}
	Data.prototype = {
		nextPage:function(){
            // 列表页数据获取
			var that = this;
			if (that.busy || that.complete)  {
				return;
			} else {
				that.busy = true;
			}
			$http.post('assistant/list', 
				{
					'category': that.id,
					'page' : that.after
				}).success(function(data){
				if ( data == undefined ) {
					alert("获取数据失败");
				}else{
					if (data.length == 0)
						that.complete = true;
					else
						angular.forEach(data,function(data){
					    		
							var obj = offerService.offerPriceLocation(data.offers);
							data.price = obj['offerprice'];
							data.locations = obj['locations'];
							data.poolrooms = offerService.poolroomsDisplay(obj['poolrooms']);
							data.latestOffer = offerService.formatLatestOffer(
									offerService.latestOffer(data.offers));
							data.discount = true;
							that.listData.push(data);
	
						});
					if (that.actor != null)
						that.actor();
	            }
				that.after += 1;
				that.busy = false;
			}.bind(this));
		},
		detail:function(callback){
            // 详细页数据获取
			var that = this;

            $http.post('assistant/' + that.id,
                {
                    'id' : that.id
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{
                	that.person = data[0];
                	
                	$http.get('assistant/' + that.id + '/stats').success(function(stats){
                		if (stats['code'] == 0){
        	    			that.person.pageview = stats['pageview'];
        	    			that.person.likes = stats['likes'];
        	    		}
                	});
                	
                	$http.get('assistant/' + that.id + '/offer').success(function(data){
                		that.offers = data[0];
                		callback();
                	});
                }
            }.bind(this)); 

		},
        praise:function(message){
            //  在详细页评论，赞的功能提交
            var that = this;

            $http.post('data-file/detail.json',
                {
                    'data' : that.id,
                    'mesid': message.id
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                     message.done = true;

                }
            }.bind(this));
        },
        sendMes:function(message){
            // 留言数据提交
            var that = this;

            $http.post('data-file/detail.json',
                {
                    'id' : that.id,
                    'mesid': message.mesContent,
                    'mesid': message.mesIcon,
                    'mesid': message.mesImg
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                    that.message.push(data.message[0]);

                    message.mesContent = "";
                    message.mesIcon = "";
                    message.mesImg = "";
                    angular.element('.action-file').val("");

                }
            }.bind(this));
        },
        order:function(){
            // 订单列表页获取
            var that = this;

			if (that.busy)  {
				return;
			} else {
				that.busy = true;
			}

            $http.post('user/order', 
                {
                    'page' : that.after
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{
                	
                    angular.forEach(data,function(data){
                    	data.discount = true;
						that.orderData.push(data);

					});
                    that.after += 1;
        		    that.busy = false;
                }
            }.bind(this));
        },
        orderDetail:function(callback){
            // 订单详细页获取
        	var that = this;
        	$http.post('assistant/order/' + that.id, 
                {
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

					that.orderData = data[0];

                    callback();

                }
            }.bind(this));
        },
        orderCansel:function(callback){
            // 订单取消提交
            var that = this;
            $http.post('assistant/order/' + that.id + '/cancel', 
                {
                }).success(function(data){
                if (data['code'] == 1)
                	callback();
            }.bind(this));
        },
	}
	return Data;
})
.directive('errormsg', function($compile, $parse) {
    return {
      restrict: 'E',
      link: function(scope, element, attr) {
        scope.$watch(attr.content, function() {
          element.html($parse(attr.content)(scope));
          $compile(element.contents())(scope);
        }, true);
      }
    }
  })
.config(function($routeProvider){
	$routeProvider
	.when('/list/:id',{
		controller:'ListCtrl',
		templateUrl:staticurl + 'list.html'
	})
	.when('/detail/:id',{
		controller:'DetailCtrl',
		templateUrl:staticurl + 'detail.html'
	})
	.when('/order/:id',{
		controller:'OrderCtrl',
		templateUrl:staticurl + 'order.html'
	})
	.when('/order_detail/:id',{
		controller:'OrderDetailCtrl',
		templateUrl:staticurl + 'order_detail.html'
	})
	 .otherwise({
	 	redirectTo:'/list/all'
	 });
})
.config( [
    '$compileProvider',
    function( $compileProvider )
    {   
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|geo|maps|tel):/);
    }
])
.controller('globalCtrl',function($scope,$rootScope,Data){

    $scope.fixed = false;
    $scope.navigation = false;

    $scope.navShow = function(){
        if ( $scope.navigation ) {
            $scope.fixed = false;
            $scope.navigation = false;
        }else{
            $scope.fixed = true;
            $scope.navigation = true;
        }
    };
})
.controller('ListCtrl',function($scope,$rootScope,Data,$routeParams,$location,scopeService){
    
    $scope.reddit = new Data($routeParams.id, function(){
    	fetchBMapLocation(function(mypoint) {
    		scopeService.safeApply($rootScope, function() {
    			for (var i = 0; i < $scope.reddit.listData.length; i++) {
    				$scope.reddit.listData[i].distance = calcDistance(mypoint, $scope.reddit.listData[i].locations)['distanceLabel'];
    			}
    		});
    	});
    });
    $scope.loadingComplete = $scope.reddit.complete;
    
    var id = $routeParams.id;
	$scope.filter = [
		{
			"title":"全部",
			"href":"all",
			"active":true
		},
//		{
//			"title":"附近",
//			"href":"nearby",
//			"active":false
//		},
		{
			"title":"人气",
			"href":"hot",
			"active":false
		},
		{
			"title":"推荐",
			"href":"recommend",
			"active":false
		}
	];

	angular.forEach($scope.filter,function(filter){
        if (filter.href == id ) {
            filter.active = true;
        }else{
            filter.active = false;
        }
	});

})
.controller('DetailCtrl',function($scope,$rootScope,$http,Data,$routeParams,$window,offerService,scopeService,$location,$route){
	$scope.detail = new Data($routeParams.id);

	$scope.detail.detail(function(){
        $scope.bookShow = false;
        $scope.callShow = false;
        $scope.comentShow = false;

        $scope.person = $scope.detail.person;
        
        $scope.poolroomTel = function() {
        	return $scope.getOffer().poolroom.tel;
        };
        $scope.maplink = function() {
        	return mapURI($scope.getOffer().poolroom.lat, $scope.getOffer().poolroom.lng);
        };
        
        var offers = $scope.detail.offers;
        var pricelocation = offerService.offerPriceLocation(offers);
		 
		$scope.locations = pricelocation['locations'];
		$scope.offerprice = pricelocation['offerprice'];
		$scope.offerlocation = offerService.poolroomsDisplay(pricelocation['poolrooms']);
        $scope.latestOffer = offerService.latestOffer(offers);
        $scope.formatLatestOffer = offerService.formatLatestOffer;
        
        $scope.offerdays = function() {
			var offerdays = offerService.offerDays(offers);
			if (offerdays.length > 0) {
				$scope.selectedOffer = offerdays[0];
				$scope.selectedOfferHour = offerdays[0].hours[0];
			}
			return offerdays;
		}(offers);
        
        $scope.getOffer = function() {
			if ($scope.selectedOffer.offer.length == 1)
				return $scope.selectedOffer.offer[0];
			for (var i = 0; i < $scope.selectedOffer.offer.length; i++) {
				var selected = moment().startOf("hour").hour($scope.selectedOfferHour);
				var start = setTime($scope.selectedOffer.offer[i].starttime, moment());
				var end = setTime($scope.selectedOffer.offer[i].endtime, moment());
				if (selected.diff(start) > 0 && end.diff(selected) > 0)
					return $scope.selectedOffer.offer[i];
			}
		};
		
		fetchBMapLocation(function(mypoint) {
    		scopeService.safeApply($rootScope, function() {
    			$scope.distance = calcDistance(mypoint, $scope.locations)['distanceLabel'];
    		});
    	});

        $scope.mes = {
            mesContent:"",
            mesIcon:"",
            mesImg:""
        };

        var winScrollTop,
            elementBottom,
            elem = angular.element('.action-book');

        angular.element($window).bind('scroll',function($window){

            winScrollTop = $(window).scrollTop();
            elementBottom = elem.offset().top + 166;

            if (winScrollTop > elementBottom) {

                $scope.$apply(function(){
                    $scope.bookbox = true;
                });

            }else{

                $scope.$apply(function(){   
                    $scope.bookbox = false;
                });

            }
        });

        $scope.bookPopup = function(){
            $scope.fixed = true;
            $scope.bookShow = true;
        };

        $scope.telphone = function(){
            $scope.callShow = true;
            $scope.fixed = true;
        }
        $scope.comment = function(){
            $scope.comentShow = true;
        }
        $scope.praise = function(message){

            $scope.detail.praise(message);
        }

        $scope.gomes = function(){

            $scope.mes.mesImg = angular.element('.action-file').val();

            if (!$scope.mes.mesContent && !$scope.mes.mesIcon && !$scope.mes.mesImg) {
                return false
            }else{
                $scope.detail.sendMes($scope.mes);
            }
        }
        
		$scope.getDayLabel = function(offerday) {
			var dayofweek = offerday.day.format('D号(ddd)');
			var prefix = "";
			switch (parseInt(offerday.idx)) {
			case 0:
				prefix = "今天";
				break;
			case 1:
				prefix = "明天";
				break;
			case 2:
				prefix = "后天";
				break;
			}
			return prefix + " " + dayofweek;
		};
		
		$scope.bookingDurations = [
		                        {   
		                                "id":"1",
		                                "name":"1"
		                        },  
		                        {   
		                                "id":"2",
		                                "name":"2"
		                        },  
		                        {   
		                                "id":"3",
		                                "name":"3"
		                        },  
		                        {   
		                                "id":"4",
		                                "name":"4"
		                        }   
		                ];

        $scope.book = {
            id:$routeParams.id,
            bookDate:$scope.selectedOffer,
            bookTime:$scope.selectedOffer.hours[0],
            bookDuration: $scope.bookingDurations[0],
            total:$scope.getOffer().price
        };

        $scope.distanceTime = 54;
        $scope.distanceDate = 54;
        $scope.derationdis= 54;

        var touch,startY,startTop,num = 0,remainder,moveNum,
            moveHeight=54,
            endTime = parseInt($scope.book.bookTime) + parseInt($scope.book.bookDuration.name);

        $scope.bookVal = $scope.getDayLabel($scope.book.bookDate) +"  "+ $scope.book.bookTime +":00 - "+endTime+":00";

        $scope.dateHammer = function(event){
            var touch = event.pointers[0],
                distance;
            if (num == 0 ) {

                startY = touch.pageY;
                startTop = angular.extend($scope.distanceDate);
                num++

            };

            dataLength = $scope.offerdays.length-2;

            distance = touch.pageY - startY + startTop;

            if (distance >= -dataLength*moveHeight && distance <= moveHeight) {

                $scope.distanceDate = angular.extend(distance);

            };
            remainder = Math.round($scope.distanceDate/54);

            if (event.isFinal) {

                $scope.distanceDate = remainder*54;

                
                if (remainder > 0) {
                	$scope.selectedOffer = $scope.offerdays[remainder-1];
                }
                if (remainder <= 0) {
                	$scope.selectedOffer = $scope.offerdays[Math.abs(remainder)+1];
                }
                $scope.book.bookDate =  $scope.selectedOffer;
               num = 0;
            };
        }

        
        $scope.timeHammer = function(event){
            var touch = event.pointers[0],
                distance;
            if (num == 0 ) {

                startY = touch.pageY;
                startTop = angular.extend($scope.distanceTime);
                num++
            };
            

            dataLength = $scope.selectedOffer.hours.length-2;

            distance = touch.pageY - startY + startTop;

            if (distance >= -dataLength*moveHeight && distance <= moveHeight) {

                $scope.distanceTime = angular.extend(distance);

            };


            remainder = Math.round($scope.distanceTime/54);

            if (event.isFinal) {

                $scope.distanceTime = remainder*54;

                
                if (remainder > 0) {
                	$scope.selectedOfferHour =  $scope.selectedOffer.hours[remainder-1]
                }
                if (remainder <= 0) {

                	$scope.selectedOfferHour =  $scope.selectedOffer.hours[Math.abs(remainder)+1];
                }
                $scope.book.bookTime = $scope.selectedOfferHour;
               
               num = 0;

            };
        }
        
        $scope.offerDuring = 1;
        $scope.durationHammer = function(event){
            var touch = event.pointers[0],
                distance;
            if (num == 0 ) {

                startY = touch.pageY;
                startTop = angular.extend($scope.derationdis);
                num++
            };
            

            dataLength = $scope.bookingDurations.length-2;

            distance = touch.pageY - startY + startTop;

            if (distance >= -dataLength*moveHeight && distance <= moveHeight) {

                $scope.derationdis = angular.extend(distance);

            };


            remainder = Math.round($scope.derationdis/54);

            if (event.isFinal) {

                $scope.derationdis = remainder*54;

                
                if (remainder > 0) {
                	$scope.book.bookDuration = $scope.bookingDurations[remainder-1]
                    
                }
                if (remainder <= 0) {
                	$scope.book.bookDuration = $scope.bookingDurations[Math.abs(remainder)+1];
                }
                $scope.offerDuring = $scope.book.bookDuration.name;

               num = 0;

            };
        }

        $scope.cansel = function(){
            $scope.fixed = false;
            $scope.bookShow = false;
            $scope.callShow = false;
        };

        $scope.ok = function(){

            endTime = parseInt($scope.book.bookTime) + parseInt($scope.book.bookDuration.name);

            if (endTime > 24 ) {
                endTime = endTime - parseInt(endTime/24) * 24;
            };

            $scope.book.total = $scope.getOffer().price * $scope.book.bookDuration.name;
            $scope.bookVal = $scope.getDayLabel($scope.book.bookDate) +"  "+ $scope.book.bookTime +":00 - "+endTime+":00";
            
            $scope.fixed = false;
            $scope.bookShow = false;
            $scope.callShow = false;
        }

        $scope.userinfo = {};
        $scope.bookBtn = function() {
        	var params = {offerDay: $scope.selectedOffer.day.unix(), offerHour: $scope.selectedOfferHour, offerDuring: $scope.offerDuring};
        	$http.post('assistant/' + $scope.detail.id + '/offer/booking', params).success(function(rt){
        		if (rt.code == 0) {
        			if (isWechat())
        				window.location = rt.payurl;
        			else
        				_AP.pay(rt.payurl);
        		}
        		else {
        			switch(rt.code){
        			case 1:
        				$scope.bookingErrMessage = "此时段已被其他用户预订，请选择其他时段";
        				break;
        			case 2:
        				$scope.bookingErrMessage = "你已经预订了此时段，去<a href=\"javascript:void(0)\" ng-click=\"goMyOrder()\">订单中心</a>查看";
        				break;
        			case 16:
        				$scope.bookingErrMessage = null;
        				$scope.updateInfo = function() {
        					$http.post('user/completeInfo', 
        						{tel: $scope.userinfo.cellphone, email: $scope.userinfo.email})
        						.success(function(data) {
        							if (data['code'] == 0) {
        								$scope.cancelUpdateInfo();
        								$route.reload();
        							}
        						});
        				};
        				$scope.cancelUpdateInfo = function() {
        					$scope.completeInfo = false;
        				};
        				$scope.completeInfo = true;
        				break;
        			default:
        				$scope.bookingErrMessage = "服务器错误，请稍后再试";
        			break;
        			}
        		}
        	}).
        	error(function(data, status, headers, config) {
        		// called asynchronously if an error occurs
        		// or server returns response with an error status.
        		if (status == 403)
        			refreshAuthentication();
        		else
        			$scope.bookingErrMessage = "服务器错误，请稍后再试";
        	});
		};
		
		$scope.goMyOrder = function() {
			$location.path('/order/all');
		};
    });
})
.controller('OrderCtrl',function($scope,$rootScope,Data,$routeParams){
	
    $scope.order = new Data($routeParams.id);
    
    $scope.createTime = function(order) {
    	return parseTime(order.createdDate).format('YYYY-MM-DD HH:mm');
    }

    var orderTime = function(timestr) {
		return parseTime(timestr).format('HH:mm');
	};
	
	var orderDate = function(timestr) {
		return parseTime(timestr).format('YYYY-MM-DD');
	};
	
	$scope.bookingTime = function(order) {
		return orderDate(order.starttime) + " " + orderTime(order.starttime) + " - "
			+ orderDate(order.endtime) + " " + orderTime(order.endtime);
	};
	
	$scope.canPay = function(order) {
		if (_.has(order, 'transaction')) {
			if (order.transaction.state == 1 && parseTime(order.starttime).diff(moment()) > 60*60*2)
				return true;
			}
		return false;
	};
	
	$scope.pay = function(order) {
		var payurl = ORDER_URL.replace(/12345678901234567890123456789012/g, order.transaction.goods.sku);
		if (isWechat())
			window.location = payurl;
		else
			_AP.pay(payurl);		
	};
	
	$scope.orderStateDisplay = function(order) {
		switch (order.state) {
		case 2:
			return "订单已支付，等待确认";
		case 4:
			return "订单已申请退款";
		case 8:
			return "订单已取消";
		case 32:
			return "订单已确认，等待消费";
		case 256:
			return "订单已消费完成";
		case 1:
			if ($scope.canPay(order))
				return "等待支付";
			return "订单已过期";
		default:
			return "";
		}		
	};
})
.controller('OrderDetailCtrl',function($controller,$scope,$rootScope,Data,$routeParams,$route){
	$controller('OrderCtrl', {$scope: $scope});

	$scope.chargeCode = function(order) {
		if (_.has(order, 'transaction')) {
			switch (order.transaction.state) {
			case 4:
				return null;
			case 3:
				return null;
			case 2:
				if (order.state == 2)
					return null;
				return order.chargeCode;
			case 1:
				return null;
			default:
				return order.chargeCode;
			}
		}
		return null;
	};
	
	$scope.order.orderDetail(function(){
        $scope.callShow = false;
        
        $scope.poolroomTel = function() {
        	return $scope.order.orderData.poolroom.tel;
        };
        
        $scope.order.orderData.btnText = "再次预约";
        $scope.order.orderData.discount = true;
        $scope.order.orderData.map = mapURI($scope.order.orderData.poolroom.lat, $scope.order.orderData.poolroom.lng);
        
        $scope.cansel = function(){
            $scope.fixed = false;
            $scope.callShow = false;
        };
        $scope.telphone = function(){
            // $scope.fixed = true;
            $scope.callShow = true;
        };

        $scope.orderCansel = function(){

            $scope.order.orderCansel(function(){
            	$route.reload();
            });
        };
        $scope.orderPay = function(){

            $scope.pay($scope.order.orderData);
        };
    });

})