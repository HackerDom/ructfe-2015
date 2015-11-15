var Datastore = require('nedb');

var users = new Datastore('users.db');
var pdata = new Datastore('pdata.db');
var reports = new Datastore('reports.db');
users.loadDatabase();
pdata.loadDatabase();
reports.loadDatabase();

var wrap = require('./utils/co-nedb');

module.exports = {
    'users': wrap(users),
    'reports': wrap(reports),
    'pdata': wrap(pdata)
};
