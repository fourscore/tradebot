const express = require('express');
const router = express.Router();
// Send all non-api requests to angular start point for page route handling
router.get('/', function(req, res, next) {
  res.render('index.html');
});
module.exports = router;