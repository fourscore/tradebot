const express = require('express');
const router = express.Router();

var path = require('path');
var appDir = path.dirname(require.main.filename);
const graph = new require(path.join(appDir,'controllers/graph.js'));

// Set Route for api
router.get('/tasks', function(req, res, next) {
  res.send('All API endpoints will be listed here');
});

router.get('/databot', graph.getlivedata);
router.get('/datafrommongo', graph.getdata);

//getting all data from for buys and sells
router.get('/transactions', graph.gettransactions);

//delete all data from mongodb users
router.get('/cleardb', graph.deletedata);

module.exports = router;