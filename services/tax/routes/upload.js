var router = require('./../router');
var getRandomString = require('./../utils/random').getRandomString;
var db = require('./../db');
var parse = require('co-busboy');
var fs = require('fs');
var path = require('path');

var f = function *(next) {
    if (!this.user) return this.redirect('/401.html');
    if ('POST' != this.method) return yield next;

    // multipart upload
    var parts = parse(this, { limits: {fileSize: 1024 * 64} });
    var kwargs = {};
    var files = [];
    var part;

    try {
        while (part = yield parts) {
            if (part instanceof Array) {
                kwargs[part[0]] = part[1];
            } else {
                if (part.filename){
                    var name = getRandomString();
                    console.log('name: ' + name);
                    var file = path.join('data', name);
                    var stream = fs.createWriteStream(file);
                    part.pipe(stream);
                    console.log('uploading %s -> %s', part.filename, stream.path);
                    files.push([part.filename, stream.path]);
                } else {
                    return this.throw(400, 'ERROR: .file problem');
                }
            }
        }
    } catch (e) {
        console.log('error:' + e);
    }

    if (!kwargs['pdata']) return this.throw(400, 'ERROR: .pdata required');
    if (!files) return this.throw(400, 'ERROR: .file required');

    try {
        var pdata = yield db.pdata.findOne({'_id': kwargs['pdata']});
        if (!pdata) {
            return this.throw(400, 'ERROR: .pdata problem');
        }
    } catch (e) {
        return this.throw(400, 'ERROR: .pdata problem ' + e);
    }

    this.template = 'upload';
    this.context = {'pdata': pdata, 'file': name};
};

router.addRoute('/u', f, 'upload');
module.exports = f;
