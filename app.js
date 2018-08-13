var express = require("express");
var app     = express();
var path    = require("path");
const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',[__dirname+"/bot.py"]);
var datafrombot
app.get('/',function(req,res){
  res.sendFile(path.join(__dirname+'/pages/html/index.html'));
  
  
  //__dirname : It will resolve to your project folder.
});

app.get('/about',function(req,res){
  res.sendFile(path.join(__dirname+'/pages/html/about.html'));
});

app.get('/sitemap',function(req,res){
  res.sendFile(path.join(__dirname+'/pages/html/sitemap.html'));
});

app.get('/databot',function(req,res){
	pythonProcess.stdout.on('data', (data) => {
	datafrombot=data.toString()
});

console.log(datafrombot)
res.send(datafrombot);
});
//getting all data from mongodb users
app.get('/datafrommongo',function(req,res){

var MongoClient = require('mongodb').MongoClient;
	
MongoClient.connect("mongodb://localhost:27017/profitdb", function (err, db) {
    
    db.collection('exch_data', function (err, collection) {
        
         collection.find().toArray(function(err, items) {
            if(err) throw err;    
			res.send(items);           
        });
        
    });
                
});
	
});
//getting all data from for buys and sells
app.get('/datafrommongobuysandsells',function(req,res){

var MongoClient = require('mongodb').MongoClient;
	
MongoClient.connect("mongodb://localhost:27017/profitdb", function (err, db) {
    
    db.collection('tradehist', function (err, collection) {
        
         collection.find().toArray(function(err, items) {
            if(err) throw err;    
			res.send(items);           
        });
        
    });
                
});
	
});


//delete all data from mongodb users
app.get('/deletedata',function(req,res){

var MongoClient = require('mongodb').MongoClient;
	
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
	
});
app.listen(8080);

console.log("Running at Port 8080");