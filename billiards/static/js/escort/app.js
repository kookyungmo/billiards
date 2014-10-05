var escortAngularModule = angular.module("escortApp", ["ngRoute", "restangular"]);
escortAngularModule.config(function($interpolateProvider) {
	  $interpolateProvider.startSymbol('//');
	  $interpolateProvider.endSymbol('//');
	});
escortAngularModule.controller("ProviderListCtrl", ["$scope", "Restangular", function($scope, Restangular) {
	Restangular.one('assistant', 'list').get().then(function (assistants){
    	$scope.assistants = assistants;
    });
}]);