var Datastore = require('nedb');

var users = new Datastore('users.db');
var pdata = new Datastore('pdata.db');
users.loadDatabase();
pdata.loadDatabase();

var wrap = require('./utils/co-nedb');

module.exports = {
    'users': wrap(users),
    'pdata': wrap(pdata)
};
