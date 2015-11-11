var grid;
var ws;
var offset = 0;
//window.onbeforeunload = function() {return "If you leave - we deauthorize you!";}

webix.ready(function(){
    webix.ui.fullScreen();
    grid = webix.ui({
        container:"grid",
        rows: [
        {type: "line", id:'page', height:"100%", cols:[
                {id: "main", type:"clean", rows:[{id:"canvas",template:"<h2>WebSockets must be enabled</h2>"},]},
            ]
        },
    ]});
    webix.ui({
        id: "searchPopup", view:"popup", autofocus: false, width:300, top:70,
        body: {view:"list", id:"searchresult", datatype:"json",
            template:"#row#",
            data:[{"row": "hello"}, {"row": "world"}]
        }
    });
    ws = new WebSocket("ws://" + window.location.host + "/websocket");
    ws.onopen = function() {ws.send('{"action": "about"}');};
    ws.onmessage = function (evt) {
        var main = JSON.parse(evt.data);
        if (main['type'] === 'default alert alert-danger')
            webix.message(main)
        else if (main['type'] && main['type'].indexOf("default") > -1) {
            $('#createReport').removeClass('hidden');
            webix.message(main);
        } else if (main['id'] === 'searchresult') {
            webix.ui(main, $$("searchPopup"), $$("searchresult"));
            $$("searchPopup").show($("#searchField"));
        } else
            webix.ui(main, $$("main"), $$("canvas"));
        grid.resize();
    };
});

function send(action, params) {
    return ws.send(JSON.stringify({'action': action, 'params': params}));
}

$('#searchField').on('input', function(){send('search', {'text':  $(this).val()});});
function auth() {if($$('auth').validate()) send('auth', $$('auth').getValues());}
function register(){send('register', $$('auth').getValues());}
$('#showLast').click(function(){offset = 0; send('show_profiles', {'offset': 0});});
$('#showLastCrimes').click(function(){offset = 0; send('show_crimes', {'offset': 0});});
function nextCrimes() {offset += 1;send('show_crimes', {'offset': offset});}
function prevCrimes() {if (offset > 0) offset -= 1; send('show_crimes', {'offset': offset});}
function nextProfiles() {offset += 1;send('show_profiles', {'offset': offset});}
function prevProfiles() {if (offset > 0) offset -= 1; send('show_profiles', {'offset': offset});}
$('#showMyProfile').click(function(){ send('show_my_profile');});

function showCrime(e, id, trg){
    var crimeid = trg.getAttribute('data-crimeid');
    if (!crimeid) crimeid = trg.childNodes[0].getAttribute('data-crimeid');
    send('show_crime', {'crimeid': crimeid});
};

function showProfile(e, id, trg){
    var uid = trg.getAttribute('data-uid');
    if (!uid) uid = trg.childNodes[0].getAttribute('data-uid');
    send('show_profile', {'uid': uid});
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
                send('its_me', {'profileid': uid, 'info': box.getElementsByTagName("input")[0].value});
        }
    });
}

$('#createReport').click(function(){
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
            send('report', $$('crime_form').getValues());
            $$('crime_win').close();
        }
    };
});

