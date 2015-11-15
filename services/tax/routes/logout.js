var router = require('./../router');
var parse = require('co-body');
var db = require('./../db');

var f = function *(next){
    this.cookies.set('name', null);
    this.cookies.set('password', null);
    this.redirect(router.resolve('index'));
};

router.addRoute('/out', f, 'logout');
module.exports = f;
