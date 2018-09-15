const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const index = require('./routes/index');
const tasks = require('./routes/tasks'); 

const app = express();
let port = process.env.PORT || 3000 // sets a relative port

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.engine('html', require('ejs').renderFile); 

// Set Static Folder
app.use(express.static(__dirname)); 
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.use('/', index);
app.use('/api', tasks);

app.listen(port, function() {
  console.log('We have successfully connected to port: ', port);
});