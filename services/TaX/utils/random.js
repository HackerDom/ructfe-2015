/**
 * Created by pahaz_000 on 08/11/2015.
 */

function getRandomString(length) {
    return Math.round((Math.pow(36, length + 1) - Math.random() * Math.pow(36, length))).toString(36).slice(1);
}

module.exports = {
    'getRandomString': getRandomString
};
