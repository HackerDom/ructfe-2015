var nconf = require("nconf");
nconf.file({file: 'config.json'});
module.exports = nconf;
