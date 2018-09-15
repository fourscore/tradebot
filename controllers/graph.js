(function(){	
	var that = {}
	
	that.getlivedata = function(req,res){
		pythonProcess.stdout.on('data', (data) => {
			datafrombot=data.toString()
		});

		console.log(datafrombot)
		res.send(datafrombot);
	}

	that.getdata = function(req,res){
		var MongoClient = require('mongodb').MongoClient;

		MongoClient.connect("mongodb://localhost:27017", function (err, client) {
			if(err){
				console.log(err);
				return;
			}
			var collection = client.db('profitdb').collection('exch_data');

			collection.find().toArray(function(err, items) {
				if(err) throw err;
				res.send(items);
				client.close();
			});
		});
	}
	
	that.gettransactions = function(req,res){

		var MongoClient = require('mongodb').MongoClient;

		MongoClient.connect("mongodb://localhost:27017/profitdb", function (err, db) {

			db.collection('tradehist', function (err, collection) {

				 collection.find().toArray(function(err, items) {
					if(err) throw err;
					res.send(items);
				});

			});

		});

	}
	
	that.deletedata = function(req,res){
		var MongoClient = require('mongodb').MongoClient;
		MongoClient.connect("mongodb://localhost:27017/profitdb", function (err, db) {
			db.collection('exch_data', function (err, collection) {
				collection.deleteMany(function(err, result) {
					if(err) throw err;
					console.log('Document Removed Successfully');
					res.send("Document deleted");
				});
			});
		});
	}

	module.exports = that;
})();
