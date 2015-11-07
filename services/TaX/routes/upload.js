var router = require('./../router');
var parse = require('co-busboy');
var fs = require('fs');
var path = require('path');

var f = function *(next) {
    if (!this.user) return this.redirect('/401.html');
    if ('POST' != this.method) return yield next;

    // multipart upload
    var parts = parse(this);
    var kwargs = {};
    var files = [];
    var part;

    while (part = yield parts) {
        if (part instanceof Array) {
            kwargs[part[0]] = part[1];
        } else {
            var file = path.join('data', Math.random().toString());
            var stream = fs.createWriteStream(file);
            part.pipe(stream);
            console.log('uploading %s -> %s', part.filename, stream.path);
            files.push([part.filename, stream.path]);
        }
    }

    // TODO: this!
    this.redirect('/');
};

router.addRoute('/u', f, 'upload');
module.exports = f;
