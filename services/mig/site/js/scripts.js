$.fn.serializeObject = function()
{
    var obj = {};
    $.each(this.serializeArray(), function() {
        if (obj[this.name] !== undefined) {
            if (!obj[this.name].push) {
                obj[this.name] = [obj[this.name]];
            }
            obj[this.name].push(this.value || "");
        } else {
            obj[this.name] = this.value || "";
        }
    });
    return obj;
};

$(function() {
    if(!window.localStorage) {
        alert("Update your browser!");
    }

    function htmlEncode(value) {
        return $('<div/>').text(value).html();
    }

    function tryParseJson(text) {
        if(!text || !text.length)
            return undefined;
        try {
            return JSON.parse(text);
        } catch(e) {
            return undefined;
        }
    }

    function setLogin() {
        var auth = $.cookie("auth");
        if(auth) {
            var login = auth.substr(Math.max(0, auth.indexOf(":")) + 1);
            $("#auth-done").text(login).show();
            $("#form-auth").hide();
        }
    }

    setLogin();

    $("form").submit(function() {
        var $form = $(this);
        var data = $form.serializeObject();
        var $error = $form.find(".error").stop(true, true).hide();
        var $inputs = $form.find("input").attr("disabled", true);
        var serialize = $form.data("serialize");
        $.ajax({
            url: $form.data("action"),
            method: "POST",
            timeout: 5000,
            data: serialize ? serialize(data) : JSON.stringify(data)
        }).done(function(text) {
            var done = $form.data("done");
            if(done) done(text);
        }).fail(function(xhr) {
            var error = xhr.responseText;
            $inputs.filter(":not([data-disabled=true])").attr("disabled", false);
            $error.text(error || "Unknown error").stop(true, true).show(200).delay(3000).hide(200);
        });
        return false;
    });

    $("#form-auth").data("done", function() {
        setLogin();
    });

    var $fields = $("#fields");

    function setBtns(prev, next) {
        $("#prev").attr("disabled", prev === false).attr("data-disabled", prev === false);
        $("#next").attr("disabled", next === false).attr("data-disabled", next === false);
    }

    function setFields(fields) {
        if(!fields) return;
        $fields.html("");
        for(var i = 0; i < fields.length; i++) {
            var field = fields[i];
            var name = htmlEncode(field.name || "");
            var value = htmlEncode(field.value || "");
            var title = htmlEncode(field.title || "");
            var len = Number(field.maxlen || 64);
            var rows = Number(field.rows || 0);
            var pattern = htmlEncode(field.pattern || "");
            var patternAttr = pattern ? " pattern='" + pattern + "'" : "";
            var titleAttr = pattern ? " title='Must match format " + pattern + "'" : "";
            var readonly = field.ro ? " readonly" : "";
            var $field = rows > 0 ?
                $("<textarea type='text' name='" + name + "' placeholder='" + title + "' maxlength='" + len + "' rows='" + rows + "'" + patternAttr + titleAttr + readonly + ">" + value + "</textarea>") :
                $("<input type='text' name='" + name + "' value='" + value + "' placeholder='" + title + "' maxlength='" + len + "'" + patternAttr + titleAttr + readonly + "/>")
            $fields.append($field);
        }
    }

    var $wzrd = $("#form-wzrd");
    $wzrd.find("input[type=submit]").click(function() {
        var $btn = $(this);
        $btn.closest("form").data("page", $btn.attr("id"))
    });
    $wzrd.data("serialize", function(data) {
        var action = $wzrd.data("page") || "load";
        return JSON.stringify({action: action, fields: data, state: localStorage.getItem("state") || ""});
    }).data("done", function(text) {
        var data = tryParseJson(text);
        if(!data)
            fail(text)
        else {
            localStorage.setItem("state", data.state || "");
            setBtns(data.prev, data.next);
            setFields(data.fields);
        }
    }).submit();

    var $last = $("#last-join");
    if($last.length) {
        function updateLast() {
            $.ajax({
                url: "/last/",
                timeout: 5000
            }).done(function(text) {
                $last.html("");
                var last = tryParseJson(text);
                for(var i = 0; i < last.length; i++) {
                    var obj = last[i];
                    for(var key in obj)
                    var $div = $("<div/>");
                    $div.append(htmlEncode(obj[key]) + "&emsp;" + htmlEncode(key));
                    $last.append($div)
                }
            }).fail(function() {
                $last.html("Error")
            }).always(function() {
                setTimeout(updateLast, 60000);
            });
        }
        updateLast();
    }
});
