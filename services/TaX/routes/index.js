var router = require('./../router');
var parse = require('co-body');
var db = require('./../db');

var f = function *(next){
    {
        this.template = 'index';
        var datalist = yield db.pdata.find({'user': this.user.name});
        this.context = {'datalist': datalist};
    }
};

router.addRoute('/', f, 'index');
module.exports = f;
