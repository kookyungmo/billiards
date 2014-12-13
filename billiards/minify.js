var compressor = require('node-minify');

new compressor.minify({
  type: 'yui-js',
  publicFolder: 'static/js/',
  fileIn: [
    'jquery.scrollUp.js',
    'app.js',
  ],
  fileOut: 'static/js/app.min.js',
  callback: function(err, min) {
	  if (err != null) {
		  console.log(err);
		  process.exit(-1);
	  }
  }
});

new compressor.minify({
	  type: 'yui-js',
	  publicFolder: 'static/js/escort/',
	  fileIn: [
	           'app.js',
	           'list.js',
	         ],
	  fileOut: 'static/js/escort/app.min.js',
	  callback: function(err, min) {
		  if (err != null) {
			  console.log(err);
			  process.exit(-1);
		  }
	  }
	});
