var path = require('path');
var name_to_func = {}; // index -> index-function
var uri_to_func = {}; // / -> index-function
var path_to_func = {}; // routes.index -> index-function
var os = require('os');
var regex = new RegExp("^[A-Z-]+[.][A-Z-]+$", "i");

function debug() {
    "use strict";
    console.log.apply(this, arguments);
}

function resolve(name) {
    "use strict";
    if (name_to_func[name]) {  // by name
        return name_to_func[name].uri;
    } else if (name.indexOf("/") > -1 && uri_to_func[name]) {  // by uri
        return uri_to_func[name].uri;
    } else if (regex.test(name)) {
        try {
            require("./" + name.replace('.', '/'));
        } catch (e) {

        }

        if (path_to_func[name]) return path_to_func[name].uri;
    }

    return null;
}


function _getCallerFile() {
    try {
        var err = new Error();
        var callerfile;
        var currentfile;

        Error.prepareStackTrace = function (err, stack) {
            return stack;
        };

        currentfile = err.stack.shift().getFileName();

        while (err.stack.length) {
            callerfile = err.stack.shift().getFileName();

            if (currentfile !== callerfile) return callerfile;
        }
    } catch (err) {
    }
    return undefined;
}


function addRoute(uri, func, name) {
    "use strict";
    console.log('addRoute', uri);
    var _path = _getCallerFile().replace(__dirname, '').split(path.sep);
    _path = _path.filter(function (v) {
        return !!v;
    });
    _path = _path.join('.').replace('.js', '');

    uri_to_func[uri] = func;
    if (name) name_to_func[name] = func;
    path_to_func[_path] = func;
    func.uri = uri;
}

function routes() {
    var router = {};

    var dispatch = function *dispatch(next) {
        var _path = this.routerPath || this.path;
        var func = uri_to_func[_path];
        if (func) {
            debug('dispatch()', this.method, this.path);
            if (func.constructor.name === 'GeneratorFunction') {
                next = func.call(this, next);
            } else {
                next = Promise.resolve(func.call(this, next));
            }
        }

        if (typeof next.next === 'function') {
            yield *next;
        } else {
            yield next;
        }
    };

    dispatch.router = router;

    return dispatch;
}


function discover (name) {
    "use strict";

    var fs = require('fs');
    var path = require('path');
    var _path = path.join(__dirname, name);
    console.log(_path);

    var walker  = fs.readdir(_path, function(err, files) {
        // Add this file to the list of files
        if (files){
            for (var f in files) {
                var file = files[f];
                require('./' + name + "/" + file)
            }
        }
    });
}

module.exports = {
    'addRoute': addRoute,
    'resolve': resolve,
    'routes': routes,
    'discover': discover
};
