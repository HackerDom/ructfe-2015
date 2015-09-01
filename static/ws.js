var grid;
webix.ready(function(){
    webix.ui.fullScreen();
    webix.ui({type:"header", template:"Ministry of Truth", css:"header"})
    grid = webix.ui({rows: [
        {type: "line", id:'page', height:"100%", cols:[
                {
                    view: "menu", layout: 'y', id: "menu", maxWidth:200, minWidth:100,
                    height:'auto',on: {onItemClick: menuChoice},
                    data: [
                        {id:"showAll",value: "All truth",icon: "eye"},
                        {id:"showSecond",value:"second truth",icon:"hourglass-2"},
                        {$template: "Spacer"},
                        {id:"createReport",value:"Report a crime",icon:"balance-scale"},
                    ]
                },
                {id: "main", type:"clean", rows:[{id:"stub",template:"<h2>WebSockets must be enabled</h2>"},]}
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
        webix.ui(main, $$("main"), $$("stub"));
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


function showAll(){
    ws.send(
        JSON.stringify({'action': 'show_all'})
    );
};
