var grid;
var offset = 0;
webix.ready(function(){
    webix.ui.fullScreen();
    webix.ui({type:"header", template:"Ministry of Truth", css:"header"})
    grid = webix.ui({rows: [
        {type: "line", id:'page', height:"100%", cols:[
                {
                    view: "menu", layout: 'y', id: "menu", maxWidth:200, minWidth:100,
                    height:"auto",on: {onItemClick: menuChoice}, css: "menu",
                    data: [
                        {id:"showLast",value: "Last persons",icon: "eye"},
                        {id:"showLastCrimes",value:"Last crimes",icon:"hourglass-2"},
                        {$template: "Spacer"},
                        {id:"createReport",value:"Report a crime",icon:"balance-scale"},
                    ]
                },
                {id: "main", type:"clean", rows:[{id:"canvas",template:"<h2>WebSockets must be enabled</h2>"},]}
            ]
        },
   ]});
});


var ws = new WebSocket("ws://localhost:1984/websocket");
ws.onopen = function() {
   ws.send('{"action": "hello"}');
};
ws.onmessage = function (evt) {
    var main = JSON.parse(evt.data);
    if (main['type'] === 'error' || main['type'] === 'default')
        webix.message(main)
    else
        webix.ui(main, $$("main"), $$("canvas"));
    grid.resize();
};

function submit() {
    if($$('auth').validate())
        ws.send(
            JSON.stringify({'action': 'auth', 'params': $$('auth').getValues()})
        );
};

function register(){
    ws.send(
        JSON.stringify({'action': 'register', 'params': $$('auth').getValues()})
    );
}

function menuChoice(id) {
    window[id]();
};

function createReport (){
    alert("Crime!!!");
};


function showLast(){
    offset = 0;
    ws.send(
        JSON.stringify({'action': 'show_profiles', 'params': {'offset': 0}})
    );
};

function nextProfiles() {
    offset += 1;
    ws.send(
        JSON.stringify({'action': 'show_profiles', 'params': {'offset': offset}})
    );
}

function prevProfiles() {
    if (offset > 0)
        offset -= 1;
    ws.send(
        JSON.stringify({'action': 'show_profiles', 'params': {'offset': offset}})
    );
}

function showProfile(e, id, trg){
    ws.send(
        JSON.stringify({'action': 'show_profile', 'params': {'uid': trg.getAttribute('data-uid')}})
    );
};