/**
 * Created by pahaz_000 on 18/11/2015.
 */

var c = require("crypto");

function md5 (data) {
    "use strict";
    return c.createHash("md5").update(data).digest("hex");
}

module.exports = {
    'md5': md5
};
