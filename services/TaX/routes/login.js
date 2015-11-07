var router = require('./../router');
var parse = require('co-body');
var db = require('./../db');

var f = function *(next){
    if ('POST' != this.method) {
        this.template = 'login';
        this.context = {};
    } else {
        var body = yield parse(this, { limit: '1kb' });
        if (!body.name) this.throw(400, '.name required');
        if (!body.password) this.throw(400, '.password required');
        var user = yield db.users.findOne({'name': body.name, 'password': body.password});
        if (user) {
            this.cookies.set('name', body.name);
            this.cookies.set('password', body.password);
            this.redirect(router.resolve('index'));
        } else {
            this.throw(401, 'O_o');
        }
    }
};

router.addRoute('/l', f, 'login');
module.exports = f;
