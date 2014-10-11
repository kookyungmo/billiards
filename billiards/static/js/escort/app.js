var escortAngularModule = angular.module("escortApp", ["ngRoute", "restangular"]);
escortAngularModule.config(function($interpolateProvider, $routeProvider) {
	  $interpolateProvider.startSymbol('<{');
	  $interpolateProvider.endSymbol('}>');
	});
escortAngularModule.controller("ProviderListCtrl", ["$scope", "Restangular", function($scope, Restangular) {
	Restangular.one('assistant', 'list').get().then(function (assistants){
    	$scope.assistants = assistants;
    	
    	var geolocation = new BMap.Geolocation();
		geolocation.getCurrentPosition(function(r){
			if(this.getStatus() === BMAP_STATUS_SUCCESS){
				for (var i = 0; i < $scope.assistants.length; i++) {
					$scope.assistants[i].distance = formatDistance(distance(r.point, new BMap.Point(
							$scope.assistants[i].poolroom.lng, $scope.assistants[i].poolroom.lat
						)));
				}
				$scope.$apply();
			}
		}, {enableHighAccuracy: false});
    });
}]);
escortAngularModule.controller('DetailCtrl', ['$scope', '$routeParams', "Restangular", function($scope, $routeParams, Restangular) {
	$scope.init = function(uuid)
	  {
		Restangular.one('assistant', uuid).post().then(function (assistant){
			escort = assistant[0];
			escort.age = _calculateAge(escort.birthday);
	    	$scope.assistant = escort;
	    });
	  };
	  
	function _calculateAge(birthday) { // birthday is a date
	    var ageDifMs = Date.now() - new Date(birthday).getTime();
	    var ageDate = new Date(ageDifMs); // miliseconds from epoch
	    return Math.abs(ageDate.getUTCFullYear() - 1970);
	}
}]);