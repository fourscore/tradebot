var express = require("express");
var app     = express();
var path    = require("path");
const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',[__dirname+"/bot.py"]);

app.get('/',function(req,res){
  res.sendFile(path.join(__dirname+'/pages/html/index.html'));
  pythonProcess.stdout.on('data', (data) => {
  console.log(data.toString())
	
});
  
  //__dirname : It will resolve to your project folder.
});

app.get('/about',function(req,res){
  res.sendFile(path.join(__dirname+'/pages/html/about.html'));
});

app.get('/sitemap',function(req,res){
  res.sendFile(path.join(__dirname+'/pages/html/sitemap.html'));
});

app.listen(3000);

console.log("Running at Port 3000");