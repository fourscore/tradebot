var app = angular.module('myApp', []);
app.controller('myCtrl', function($scope) {
$scope.function2=function()
{
console.log("godjdks")
$http.get('/databot').then(function(res){
					
$scope.listofconfig=res.data
console.log($scope.listofconfig);
				});
}
	
});
			
		