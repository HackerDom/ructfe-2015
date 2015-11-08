var router = require('./../router');
var parse = require('co-body');
var db = require('./../db');

var f = function *(next){
    if (!this.user) return this.redirect(router.resolve('login') + '?next=index');
    this.template = 'index';
    var datalist = yield db.pdata.find({'user': this.user.name});
    this.context = {'datalist': datalist};
};

router.addRoute('/', f, 'index');
module.exports = f;
