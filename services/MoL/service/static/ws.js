var grid;
var ws;
var offset = 0;

webix.ready(function(){
    webix.ui.fullScreen();
    webix.ui({cols: [
        {template:"Ministry of Love <span class='webix_icon fa-heartbeat'></span>", css:"header"},
        {view: 'search', placeholder: "Search...", id: "searchField", width:300, css:"header", on:{"onTimedKeyPress": search}},
    ]});
    grid = webix.ui({rows: [
        {type: "line", id:'page', height:"100%", cols:[
                {
                    view: "menu", layout: 'y', id: "menu", maxWidth:200, minWidth:100,
                    height:"auto",on: {onItemClick: menuChoice}, css: "menu",
                    data: [
                        {id:"showLast",value: "People",icon: "users"},
                        {id:"showLastCrimes",value:"Last crimes",icon:"hourglass-2"},
                        {$template: "Separator"},
                        {id:"showMyProfile",value:"My Profile",icon:"user"},
                        {$template: "Separator"},
                        {$template: "Spacer"},
                        {id:"createReport",value:"Report a crime",icon:"bullhorn"},
                    ]
                },
                {id: "main", type:"clean", rows:[{id:"canvas",template:"<h2>WebSockets must be enabled</h2>"},]},
            ]
        },
    ]});
    $$('menu').hideItem('createReport');
    webix.ui({
        id: "searchPopup", view:"popup", autofocus: false, width:300,
        body: {view:"list", id:"searchresult", datatype:"json",
            template:"#row#",
            data:[{"row": "hello"}, {"row": "world"}]
        }
    });
    ws = new WebSocket("ws://localhost:1984/websocket");
    ws.onopen = function() {ws.send('{"action": "hello"}');};
    ws.onmessage = function (evt) {
        var main = JSON.parse(evt.data);
        if (main['type'] === 'error')
            webix.message(main)
        else if (main['type'] === 'default') {
            $$('menu').showItem('createReport');
            webix.message(main);
        } else if (main['id'] === 'searchresult') {
            webix.ui(main, $$("searchPopup"), $$("searchresult"));
            $$("searchPopup").show($$("searchField").$view);
        } else
            webix.ui(main, $$("main"), $$("canvas"));
        grid.resize();
    };
});

function search() {ws.send(JSON.stringify({'action': 'search', 'params': {'text':  this.getValue()}}));}
function auth() {if($$('auth').validate()) ws.send(JSON.stringify({'action': 'auth', 'params': $$('auth').getValues()}));}
function register(){ws.send(JSON.stringify({'action': 'register', 'params': $$('auth').getValues()}));}
function menuChoice(id) {window[id]();};
function showLast(){offset = 0; ws.send(JSON.stringify({'action': 'show_profiles', 'params': {'offset': 0}}));}
function showLastCrimes(){offset = 0; ws.send(JSON.stringify({'action': 'show_crimes', 'params': {'offset': 0}}));}
function nextProfiles() {offset += 1;ws.send( JSON.stringify({'action': 'show_profiles', 'params': {'offset': offset}}));}
function prevProfiles() {if (offset > 0) offset -= 1; ws.send(JSON.stringify({'action': 'show_profiles', 'params': {'offset': offset}}));}
function showMyProfile(){ ws.send(JSON.stringify({'action': 'show_my_profile'}));};

function showCrime(e, id, trg){
    var crimeid = trg.getAttribute('data-crimeid');
    if (!crimeid) crimeid = trg.childNodes[0].getAttribute('data-crimeid');
    ws.send(JSON.stringify({'action': 'show_crime', 'params': {'crimeid': crimeid}}));
};

function showProfile(e, id, trg){
    var uid = trg.getAttribute('data-uid');
    if (!uid) uid = trg.childNodes[0].getAttribute('data-uid');
    ws.send(JSON.stringify({'action': 'show_profile', 'params': {'uid': uid}}));
};

function itsMe(uid){
    webix.message.keyboard = false;
    var box = webix.modalbox({
        title: "Type any private information of its profile",
        buttons: ["Ok", "Cancel"],
        text: "<input type='text' />",
        width: "40%",
        callback: function(result) {
            if (result === "0")
                ws.send(JSON.stringify({'action': 'its_me', 'params': {'profileid': uid, 'info': box.getElementsByTagName("input")[0].value}}));
        }
    });
}

function createReport (){
    var report = webix.ui({
        view:"window",
        id:"crime_win",
        head: {
            type: "clean",
            view:"toolbar",
            cols:[
                {template: "Report crime"},
                {view:"icon", icon:"times", width:50, click:("$$('crime_win').close();")},
            ]
        },
        modal:true,
        move:true,
        width:420,
        position:"center",
        body:{
            view:"form",
            id:"crime_form",
            elementsConfig: {labelWidth: 120},
            elements:[
                { view:"text", placeholder:"Name", name:"name"},
                { view:"text", placeholder:"Article", name:"article"},
                { view:"text", placeholder:"City", name:"city"},
                { view:"text", placeholder:"Country", name:"country"},
                { view:"datepicker", placeholder: 'Crime Date', name:"crimedate"},
                { view:"text", placeholder:"Description", name:"description"},
                { view:"text", name:"participants", placeholder:"<profileid1>, <profileid2>, <profileid3>" },
                { view:"toggle", type:"iconButton", name:"closed",offIcon:"user-secret", offLabel:"In process", onIcon:"gavel", onLabel:"Closed", css:"button_warning", name:"closed", on: {"onChange": showJudgement}},
                { view:"text", placeholder:"Judgement", id: "judgement", name:"judgement", hidden:true},
                { view:"toggle", type:"iconButton", name:"private",offIcon:"eye", offLabel:"Public", onIcon:"eye-slash", onLabel:"Private", css:"button_success", name:"private"},
                { margin:5, cols:[
                    { view:"button", value:"Send" , css:"button_success", click:report},
                    { view:"button", value:"Cancel", click:("$$('crime_win').close();") }
                ]
                }
            ]
        }
    }).show();
    function showJudgement () {if (this.getValue())$$("judgement").show();else $$("judgement").hide();};
    function report() {
        if($$('crime_form').validate()) {
            ws.send(JSON.stringify({'action': 'report', 'params': $$('crime_form').getValues()}));
            $$('crime_win').close();
        }
    };
};

