# coding=utf-8
__author__ = 'm_messiah'

ABOUT = {
    'id': 'canvas',
    'rows': [
        {'template': """
        <div class="row about">
            <div class="col-sm-4 center-block">
                <img src="/static/logos/mol.png" class="img-responsive">
            </div>
            <div class="col-sm-8">
                <h1>Ministry of Love</h1>
                <p>
                    Love your neighbor, respect the law.<br>
                    Be careful.
                </p>
                <button class="btn btn-blank" onclick="send();">Log in</button>
            </div>
        </div>
        """}
    ]

}

AUTH_FORM = {
    'id': 'canvas',
    'rows': [
        {
            'view': "form",
            'id': "auth",
            'width': 350,
            'css': 'form-horizontal',
            'bottomPadding': 18,
            'elements': [
                {
                    'view': 'text',
                    'label': "Username",
                    'name': "username",
                    'invalidMessage': 'Username is not present',
                    'required': True,
                },
                {
                    'view': 'text',
                    'label': "Password",
                    'name': "password",
                    'type': 'password',
                    'invalidMessage': 'Password is not present',
                    'required': True,
                },
                {
                    'css': 'form-group',
                    'cols': [
                        {
                            'view': 'button',
                            'label': "Login",
                            'click': 'auth',
                            'type': 'iconButton',
                            'icon': 'sign-in',
                            'align': 'center',
                        },
                        {
                            'view': 'button',
                            'label': "Register",
                            'click': 'register',
                            'type': 'iconButton',
                            'icon': 'pencil',
                            'align': 'center',
                        },
                    ]
                },
            ],
        }
    ]
}

ERROR_MESSAGE = {'type': "default alert alert-danger"}
SUCCESS_MESSAGE = {'type': 'default alert alert-success'}
INFO_MESSAGE = {'type': 'default alert alert-info'}
WARN_MESSAGE = {'type': 'default alert alert-warning'}

PROFILES = {
    'id': 'canvas',
    'rows': [
        {
            'view': "dataview",
            'height': 800,
            'type': {
                'templateStart': "<div class='bg_panel card' data-uid='#uid#'>",
                'template': "<img class='cardImage' "
                            "src='/userpics/#userpic#.jpg' />"
                            "<div class='cardTitle'>#name# #lastname#</div>",
                'templateEnd': "</div>",
                'height': 170,
                'width': 450,
            },
            'onClick': {
                'card': 'showProfile',
            }
        },
        {
            'cols': [
                        {
                            'view': 'button',
                            'label': "<-",
                            'click': 'prevProfiles',
                            'height': 50,
                        },
                        {
                            'view': 'button',
                            'label': "->",
                            'click': 'nextProfiles',
                            'height': 50,
                        },
                    ],
        },
    ],
}

PROFILE = {
    'id': 'canvas',
    'rows': [
        {
            'view': "layout",
            'cols': [
                {
                    'maxWidth': 170,
                    'rows': [
                        {
                            "view": "button",
                            "id": "itsme",
                            "value": "It's me",
                        },
                        {
                            'height': 170,
                            'css': 'center-block',
                            'template': "<img src='/userpics/#userpic#.jpg' />"
                        },
                        {
                            "template": "<span class='webix_icon #icon# "
                                        "text_success success_icon'></span>"
                        },
                    ]
                },
                {
                    'rows': [
                                {
                                    'template': """
                        <div class='profile'>
                            <h2>#name# #lastname#</h2>
                            <dl class="dl-horizontal">
                                <dt>Birth</dt><dd>#birthdate#</dd>
                                <dt>Mobile</dt><dd>#mobile#</dd>
                                <dt>City</dt><dd>#city#</dd>
                                <dt>Marital status</dt>
                                <dd>
                                    <span class="webix_icon #marital_icon#">
                                    </span>
                                </dd>
                            </dl>
                        </div>"""
                                },
                                {
                                    'view': "datatable",
                                    'fixedRowHeight': False,
                                    'columns': [
                                        {'id': "name", 'header': "Name",
                                         'fillspace': 1},
                                        {'id': "article", 'header': "Article",
                                         'fillspace': 1},
                                        {'id': "description",
                                         "header": "Description",
                                         'fillspace': 2},
                                        {'id': "crimedate", 'header': "Date",
                                         'fillspace': 2},
                                        {'id': "city", "header": "City",
                                         'fillspace': 1},
                                        {'id': "country", "header": "Country",
                                         'fillspace': 1},
                                        {'id': "verdict", "header": "Verdict",
                                         'fillspace': 1},
                                        {'id': "participants",
                                         "header": "Participants",
                                         'fillspace': 2}
                                    ],
                                    'on': {
                                        "onresize": "webix.once(function(){"
                                                    "this.adjustRowHeight("
                                                    "'participants', true);})"
                                    },
                                },
                    ]
                },
            ]
        }
    ],
}


CRIMES = {
    'id': 'canvas',
    'rows': [
        {
            'view': "dataview",
            'height': 800,
            'type': {
                'templateStart': "<div class='bg_panel card'"
                                 "data-crimeid='#crimeid#'>",
                'template': "<div class='cardMain'>#name#: #article#</div>"
                            "<div class='cardInfo'>"
                            "#country#/#city# #crimedate#"
                            "<span class=\"webix_input_icon #public#\"></span>"
                            "</div>",
                'templateEnd': "</div>",
                'height': 170,
                'width': 450,
            },
            'onClick': {
                'card': 'showCrime',
            }
        },
        {
            'cols': [
                {
                    'view': 'button',
                    'label': "<-",
                    'click': 'prevCrimes',
                    'height': 50,
                },
                {
                    'view': 'button',
                    'label': "->",
                    'click': 'nextCrimes',
                    'height': 50,
                },
            ],
        },
    ],
}

CRIME = {
    'id': 'canvas',
    'rows': [
        {
            'template': """
                <div class='profile'>
                    <h2>#name# #article#</h2>
                    <dl class="dl-horizontal">
                        <dt>City</dt><dd>#country#/#city#</dd>
                        <dt>Date</dt><dd>#crimedate#</dd>
                        <dt>Description</dt><dd>#description#</dd>
                        <dt>Judgement</dt><dd>#judgement#</dd>
                        <dt>Closed</dt><dd>#closed#</dd>
                        <dt>Participants</dt><dd>#participants#</dd>
                    </dl>
                </div>"""
        },
    ],
}

SEARCH = {
    'id': "searchresult",
    'rows': [
        {
            'autoheight': True,
            'view': "list",
            'datatype': "json",
            'template': "<span data-uid='#profileid#'>#name# #lastname#</span>",
            "on": {'onItemClick': "showProfile"},
        },
        {
            'autoheight': True,
            'view': "list",
            'datatype': "json",
            'template': "<span data-crimeid='#crimeid#'>"
                        "#name# #crimedate#</span>",
            "on": {'onItemClick': "showCrime"},
        },
        {
            'autoheight': True,
            'view': "list",
            'datatype': "json",
            'template': "<span>#answer#</span>",
        },
    ]
}
