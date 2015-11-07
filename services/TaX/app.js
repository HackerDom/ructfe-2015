/**
 * Module dependencies.
 */

var logger = require('koa-logger');
var serve = require('koa-static');
var views = require('co-views');
var koa = require('koa');
var app = koa();
var path = require('path');
var render = views(__dirname + '/views', { ext: 'ejs' });
var router = require('./router');
var config = require('./config');
var db = require('./db');

// log requests

app.use(logger());
app.use(serve(__dirname + '/public'));
app.use(serve(__dirname + '/data'));

app.use(function *(next){
  yield next;
  if (this.body || !this.idempotent) return;
  if (this.template && this.context) {
    this.context['resolve'] = router.resolve;
    this.context['session'] = this.session;
    this.context['user'] = this.user;
    this.body = yield render(this.template, this.context);
    return;
  }
  this.redirect('/404.html');
});

var sessions = {};

app.use(function *(next){
  var s = this.cookies.get('session');
  var name = this.cookies.get('name');
  var password = this.cookies.get('password');

  if (!s) {
    s = Math.random().toString();
    this.cookies.set('session', s);
  }
  var ss = sessions[s] || {};
  sessions[s] = ss;
  this.session = ss;
  if (name && password) {
    this.user = yield db.users.findOne({'name': name, 'password': password});
  }
  yield next;
});

app.use(router.routes());

// listen
router.discover('routes');
app.listen(3000);
console.log('listening on port 3000');
