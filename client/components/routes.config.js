var botApp = angular.module('botApp', ['ngRoute']);

botApp.config(function($routeProvider){
	$routeProvider
		.when('/', {
			templateUrl : '/client/templates/dashboard.html',
			controller	: 'dashboardController'
		})
});

botApp.controller('mainctrl', function($scope){
})
