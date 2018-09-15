angular.module('botApp')
.controller('dashboardController', function($scope, $http) {
	$scope.function2=function(){
			$http.get('/databot').then(function(res){
				$scope.data="Not known"
				console.log(res.data.length)
				if(res.data.length==8){
					$scope.data="Online"
				}
				else {
					$scope.data="Offline"
				}
			});
		}
	//getting all data from mongodb users
	graph = function(){
		$http.get('/api/datafrommongo').then(function(res){

			var price=[]
			var datafordata=[]
			var volume=[]
			var i
			for(i=0;i<res.data.length;i++)
			{
				price.push(res.data[i]["price"])
				datafordata.push(res.data[i]["time"])
				volume.push(res.data[i]["volume"])

			}
			console.log('Building Graph');
			build_graphsub(datafordata,price,volume,'Price','Volume','myDiv')
		});

		/*$http.get('/api/datafrommongobuysandsells').then(function(res){
			var price=[]
			var datafordata=[]
			var volume=[]
			console.log(res.data);
			var i
		});*/
	}
	graph();

	function build_graphsub(x1,y1,y2,name1,name2,id){
		var mytitle='Money and Volume'
		var trace1 = {
			x: x1,
			y: y1,
			mode: 'lines',
			name: name1
		};

		var trace2 = {
			x: x1,
			y: y2,
			mode: 'lines',
			name: name2
		};

		var layout = {
			title:mytitle
		};
		var data = [trace1, trace2];
		Plotly.newPlot(id,data,layout);
	}

	$scope.deletedata = function(){
		$http.get('/api/deletedata').then(function(res){
			console.log("deleted database")

		});
	}
});
