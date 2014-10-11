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

moment.lang("zh-CN");

angular.module("escortApp", ["ngRoute", "restangular"])

.config(function($interpolateProvider, $routeProvider) {
	  $interpolateProvider.startSymbol('<{');
	  $interpolateProvider.endSymbol('}>');
	})

.controller("ProviderListCtrl", ["$scope", "Restangular", function($scope, Restangular) {
	Restangular.one('assistant', 'list').get().then(function (assistants){
    	$scope.assistants = assistants;
		fetchBMapLocation(function(mypoint) {
			for (var i = 0; i < $scope.assistants.length; i++) {
				$scope.assistants[i].distance = formatDistance(distance(mypoint, new BMap.Point(
						$scope.assistants[i].poolroom.lng, $scope.assistants[i].poolroom.lat
					)));
			}
			$scope.$apply();
		});
    });
}])

.controller('DetailCtrl', ['$scope', '$routeParams', "Restangular", function($scope, $routeParams, Restangular) {
	var dayRange = _.range(3);
	var buffer = 2;
	
	$scope.init = function(uuid)
	  {
		var baseEscort = Restangular.one('assistant', uuid);
		baseEscort.post().then(function (assistant){
			escort = assistant[0];
			escort.age = _calculateAge(escort.birthday);
	    	$scope.assistant = escort;
	    });
		baseEscort.getList("offer").then(function (offers){
			offers = offers[0];
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
						poolrooms.push(offers[i][j].poolroom.name);
						locations.push(new BMap.Point(
							offers[i][j].poolroom.lng, offers[i][j].poolroom.lat
						));
					}
				}
			}
			if (maxprice != minprice)
				$scope.offerprice = minprice + "-" + maxprice;
			else
				$scope.offerprice = minprice;
			
			var output = '';
			for (i=0;i<poolrooms.length;i++){
				output += poolrooms[i];
				if (i != poolrooms.length - 1)
					output += "/";
			}
			 
			$scope.offerlocation = output;
			$scope.offers = offers;
			
			function setTime(timestr, time) {
				var timearray = timestr.split(":");
				time.hour(timearray[0]);
				time.minute(0);
				return time;
			}
			// calculate latest offer
			$scope.latestOffer = function(){
				var now = moment().startOf("hour").add(1, 'h');
				var end = moment();
				var start = now.clone().add(buffer, 'h');
				for (var i in dayRange) {
					for (var j = 0; j < $scope.offers[i].length; j++) {
						if (start.diff(end, 'd') < 0) {
							return setTime($scope.offers[i][j].starttime, end);
						}
						var timearray = $scope.offers[i][j].endtime.split(":");
						end.hour(timearray[0]);
						end.minute(timearray[1]);
					}
					if (start.diff(end) < 0)
						return start;
					end.add(1, 'd');
				}
				return null;
			}();
			$scope.hasOffer = $scope.latestOffer != null;
			
			$scope.formatLatestOffer = function(start) {
				return start.calendar();
			};
			
			$scope.offerdays = function() {
				var offerdays = [];
				var starthour = moment().startOf("hour").add(buffer + 1, 'h');
				for (var i in dayRange) {
					var day = moment().startOf('day');
					day.add(i, 'd');
					hours = [];
					for (var j = 0; j < $scope.offers[i].length; j++) {
						var start, end;
						if (starthour.clone().startOf('day').diff(day, 'd') == 0) {
							start = starthour.clone();
							end = setTime($scope.offers[i][j].endtime, moment());
						} else {
							start = setTime($scope.offers[i][j].starttime, moment());
							end = setTime($scope.offers[i][j].endtime, moment());
						}
						if (end.diff(start, 'h') > 0) {
							hours = hours.concat(_.range(start.hour(), end.hour()));
						}
					}
					if (hours.length > 0) {
						offerdays.push({'hours': hours, 'day': day, 'offer': $scope.offers[i], 'idx': i});
					}
				}
				if (offerdays.length > 0) {
					$scope.selectedOffer = offerdays[0];
					$scope.selectedOfferHour = offerdays[0].hours[0];
				}
				return offerdays;
			}();
			
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
				var max = min = 0;
				for (var i = 0; i < locations.length; i++) {
					var dist = distance(mypoint, locations[i]);
					if (min == 0 || min > dist)
						min = dist;
					if (max == 0 || max < dist)
						max = dist;
				}
				if (min == max)
					$scope.offerdistance = formatDistance(min);
				else
					$scope.offerdistance = formatDistance(min) + "-" + formatDistance(max);
				$scope.$apply();
			});
		});
	  };
	  
	function _calculateAge(birthday) { // birthday is a date
	    var ageDifMs = Date.now() - new Date(birthday).getTime();
	    var ageDate = new Date(ageDifMs); // miliseconds from epoch
	    return Math.abs(ageDate.getUTCFullYear() - 1970);
	}
}]);