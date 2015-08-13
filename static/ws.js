function printTerm(term) {
    var result = [];
    result.push("<" + term.term);
    if (term.id) {result.push(" id='" + term.id + "'");}
    if (term.name) {result.push(" name='" + term.name + "'");}
    if (term.method) {result.push(" method='" + term.method + "'");}
    if (term.classes) {result.push(" class='" + term.classes + "'");}
    if (term.style) {result.push(" style='" + term.style + "'");}
    if (term.typ) {result.push(" type='" + term.typ + "'");}
    if (term.value) {result.push(" value='" + term.value + "'");}
    result.push(">");
    if (term.errors) {
        for (var i = 0; i< term.errors.length; i++) {
            result.push(printTerm(term.errors[i]));
        }
    }
    if (term.content) { result.push(term.content); }
    if (term.children) {
        for (var i = 0; i< term.children.length; i++) {
            result.push(printTerm(term.children[i]));
        }
    }
    result.push("</" + term.term + ">");
    return result.join("");
}


webix.ready(function(){
    webix.ui({container: 'header', rows: [{type:"header", template:"BB"},]});
    webix.ui({container: 'main', id: "main", rows: []});
});


var ws = new WebSocket("ws://localhost:2707/websocket");
ws.onopen = function() {
   ws.send('{"action": "hello"}');
};
ws.onmessage = function (evt) {
   var main = JSON.parse(evt.data);
   $$('main').addView(main, 0);
};
function submit() {
    var params = $$('auth').getValues()
    $$('main').removeView('auth');
    ws.send(JSON.stringify({'action': 'auth', 'params': params}));
    $$('output').show();
};




