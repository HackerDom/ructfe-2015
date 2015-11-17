/**
 * Created by pahaz_000 on 18/11/2015.
 */

function get_seconds() {
    "use strict";
    return new String(new Date().getTime()).substring(0, 10) + 1;
}

module.exports = {
    'get_seconds': get_seconds
};