var router = require('./../router');
var parse = require('co-body');
var db = require('./../db');

var f = function *(next) {
  if (!this.user) return this.redirect(router.resolve('login') + '?next=routes.users');
  if ('POST' != this.method) {
    this.template = 'user';
    var datalist = yield db.pdata.find({'user': this.user.name});
    this.context = {'datalist': datalist};
  } else {
    var body = yield parse(this, { limit: '1kb' });
    if (!body.name) this.throw(400, 'ERROR: .name required');
    if (!body.private) this.throw(400, 'ERROR: .private data required');

    yield db.pdata.insert({'name': body.name, 'private': body.private, 'user': this.user.name});
    this.redirect(router.resolve('index'));
  }
};

router.addRoute('/me', f, 'user');
module.exports = f;
