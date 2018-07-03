var http = require('http');
var fs = require('fs');

http.createServer(function (req, res) {
	fs.readFile('index.html', function(err, data) {
	    res.writeHead(200, {'Content-Type': 'text/html'});
	    res.write(data);
	    res.end();
  	});
    fs.readFile('data.json', function(err, data) {
		if (err) throw err;
		let d = JSON.parse(data);
		for (var key in d){
		    console.log(key);
		}
	});
}).listen(8080);