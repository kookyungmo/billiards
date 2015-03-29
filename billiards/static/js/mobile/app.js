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

var staticurl = 'static/m/';
angular.module('app',['ngRoute','hmTouchEvents','infinite-scroll'])
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

	var Data = function(id){

		this.id = id;

		// 导航数据
		this.navData = [];

		// 翻页
		this.busy = false;
	    this.after = 1;

		// 列表页数据 list data
		this.listData = [];
        
        // 详细页数据 detail data
	    this.person = [];
	    this.billiardsRoom = [];
	    this.orderinfo = [];
	    this.message = [];

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
			if (that.busy)  {
				return;
			} else {
				that.busy = true;
			}
			$http.post('assistant/list', 
				{
					'category': that.id,
					'after' : that.after
				}).success(function(data){
				if ( data == undefined ) {
					alert("获取数据失败");
				}else{
			 
					angular.forEach(data,function(data){
				    		
						var obj = offerService.offerPriceLocation(data.offers);
						data.price = obj['offerprice'];
						data.locations = obj['locations'];
						data.poolrooms = offerService.poolroomsDisplay(obj['poolrooms']);
						data.latestOffer = offerService.formatLatestOffer(
								offerService.latestOffer(data.offers));

						that.listData.push(data);

					})

	            }
			}.bind(this));
			that.after = this.after++;
		    that.busy = false;
		},
		detail:function(callback){
            // 详细页数据获取
			var that = this;

            $http.post('data-file/detail.json',
                {
                    'id' : that.id
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                    that.person = data.person;
                    that.billiardsRoom = data.billiardsRoom;
                    that.orderinfo = data.orderinfo;
                    that.message = data.message;

                    that.bookDate = data.bookDate;
                    that.bookTime = data.bookTime;
                    that.bookDuration = data.bookDuration;

                    callback();
                }
            }.bind(this)); 

		},
        detailBook:function(val,callback){
            //  预约数据提交
            var that = this;
            $http.post('data-file/detail.json',
                {
                    'id' : that.id,
                    "bookDate": val.bookDate,
                    "bookTime": val.bookTime,
                    "bookDuration":val.bookDuration,
                    "total":val.total
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                    alert('提交订单成功');
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

            $http.post('data-file/order.json', 
                {
                	"id":that.id,
                    'after' : that.after
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                    angular.forEach(data,function(data){

						that.orderData.push(data);

					});

                }
            }.bind(this));
            that.after = this.after++;
		    that.busy = false;
        },
        orderDetail:function(callback){
            // 订单详细页获取
        	var that = this;
        	$http.post('data-file/order_detail.json', 
                {
                	'id': that.id,
                    'after': that.after
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

					that.orderData = data;

                    callback();

                }
            }.bind(this));
        },
        orderCansel:function(){
            // 订单取消提交
            var that = this;
            $http.post('data-file/order_detail.json', 
                {
                    'id': that.id
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                    alert("取消支付...")

                }
            }.bind(this));
        },
        orderPay:function(){
            // 订单支付提交
            var that = this;
            $http.post('data-file/order_detail.json', 
                {
                    'id': that.id
                }).success(function(data){
                if (data == undefined ) {
                    alert("获取数据失败");
                }else{

                    alert("正在支付...")

                }
            }.bind(this));
        }
	}
	return Data;
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
	// .otherwise({
	// 	redirectTo:'/list/all'
	// });
})
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
.controller('ListCtrl',function($scope,$rootScope,Data,$routeParams,$location){
    
    $scope.reddit = new Data($routeParams.id);

    var id = $routeParams.id;
	$scope.filter = [
		{
			"title":"全部",
			"href":"all",
			"active":true
		},
		{
			"title":"附近",
			"href":"nearby",
			"active":false
		},
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
	
	fetchBMapLocation(function(mypoint) {
		for (var i = 0; i < $scope.reddit.listData.length; i++) {
			$scope.reddit.listData[i].distance = calcDistance(mypoint, $scope.reddit.listData[i].locations)['distanceLabel'];
		}
		$scope.$apply();
	});

})
.controller('DetailCtrl',function($scope,$rootScope,Data,$routeParams,$window){
	$scope.detail = new Data($routeParams.id);

	$scope.detail.detail(function(){
        $scope.bookShow = false;
        $scope.callShow = false;
        $scope.comentShow = false;

        $scope.person = $scope.detail.person;
        $scope.billiardsRoom = $scope.detail.billiardsRoom;
        $scope.orderinfo = $scope.detail.orderinfo;
        $scope.message = $scope.detail.message;

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

        $scope.book = {
            id:$routeParams.id,
            bookDate:$scope.detail.bookDate[0],
            bookTime:$scope.detail.bookTime[0],
            bookDuration: $scope.detail.bookDuration[0],
            total:$scope.detail.person.price
        };

        $scope.distanceTime = 54;
        $scope.distanceDate = 54;
        $scope.derationdis= 54;

        var touch,startY,startTop,num = 0,remainder,moveNum,
            moveHeight=54,
            endTime = parseInt($scope.book.bookTime.name) + parseInt($scope.book.bookDuration.name);

        $scope.bookVal = $scope.book.bookDate.name +"  "+ $scope.book.bookTime.name +":00 - "+endTime+":00";

        $scope.dateHammer = function(event){
            var touch = event.pointers[0],
                distance;
            if (num == 0 ) {

                startY = touch.pageY;
                startTop = angular.extend($scope.distanceDate);
                num++

            };

            dataLength = $scope.detail.bookDate.length-2;

            distance = touch.pageY - startY + startTop;

            if (distance >= -dataLength*moveHeight && distance <= moveHeight) {

                $scope.distanceDate = angular.extend(distance);

            };
            remainder = Math.round($scope.distanceDate/54);

            if (event.isFinal) {

                $scope.distanceDate = remainder*54;

                
                if (remainder > 0) {
                    $scope.book.bookDate =  $scope.detail.bookDate[remainder-1]
                }
                if (remainder <= 0) {

                    $scope.book.bookDate =  $scope.detail.bookDate[Math.abs(remainder)+1];
                }
               
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
            

            dataLength = $scope.detail.bookTime.length-2;

            distance = touch.pageY - startY + startTop;

            if (distance >= -dataLength*moveHeight && distance <= moveHeight) {

                $scope.distanceTime = angular.extend(distance);

            };


            remainder = Math.round($scope.distanceTime/54);

            if (event.isFinal) {

                $scope.distanceTime = remainder*54;

                
                if (remainder > 0) {
                    $scope.book.bookTime =  $scope.detail.bookTime[remainder-1]
                }
                if (remainder <= 0) {

                    $scope.book.bookTime =  $scope.detail.bookTime[Math.abs(remainder)+1];
                }
               
               num = 0;

            };
        }
        $scope.durationHammer = function(event){
            var touch = event.pointers[0],
                distance;
            if (num == 0 ) {

                startY = touch.pageY;
                startTop = angular.extend($scope.derationdis);
                num++
            };
            

            dataLength = $scope.detail.bookTime.length-2;

            distance = touch.pageY - startY + startTop;

            if (distance >= -dataLength*moveHeight && distance <= moveHeight) {

                $scope.derationdis = angular.extend(distance);

            };


            remainder = Math.round($scope.derationdis/54);

            if (event.isFinal) {

                $scope.derationdis = remainder*54;

                
                if (remainder > 0) {
                    $scope.book.bookDuration =  $scope.detail.bookDuration[remainder-1];
                }
                if (remainder <= 0) {
                    $scope.book.bookDuration =  $scope.detail.bookDuration[Math.abs(remainder)+1];
                }

               num = 0;

            };
        }

        $scope.cansel = function(){
            $scope.fixed = false;
            $scope.bookShow = false;
            $scope.callShow = false;
        };

        $scope.ok = function(){

            endTime = parseInt($scope.book.bookTime.name) + parseInt($scope.book.bookDuration.name);

            if (endTime > 24 ) {
                endTime = endTime - parseInt(endTime/24) * 24;
            };

            $scope.book.total = $scope.detail.person.price * $scope.book.bookDuration.name;
            $scope.bookVal = $scope.book.bookDate.name +"  "+ $scope.book.bookTime.name +":00 - "+endTime+":00";
            
            $scope.fixed = false;
            $scope.bookShow = false;
            $scope.callShow = false;
        }

        $scope.bookBtn = function(){
            $scope.detail.detailBook($scope.book);
        }
    });
})
.controller('OrderCtrl',function($scope,$rootScope,Data,$routeParams){
	
    $scope.order = new Data($routeParams.id);

})
.controller('OrderDetailCtrl',function($scope,$rootScope,Data,$routeParams){
	
	$scope.order = new Data($routeParams.id);
	$scope.order.orderDetail(function(){
        $scope.callShow = false;
        $scope.billiardsRoom = $scope.order.orderData;

        $scope.cansel = function(){
            $scope.fixed = false;
            $scope.callShow = false;
        };
        $scope.telphone = function(){
            // $scope.fixed = true;
            $scope.callShow = true;
        };

        $scope.orderCansel = function(){

            $scope.order.orderCansel();
        };
        $scope.orderPay = function(){

            $scope.order.orderPay();
        };
    });

})