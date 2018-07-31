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

app.listen(8080);

console.log("Running at Port 8080");