/**
 * Created by Sushant on 1/15/2015.
 */

var page = require('webpage').create(), system = require('system');
page.open(system.args[1], function() {
  page.render(system.args[2]);
  phantom.exit();
});

