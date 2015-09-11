# coding=utf-8
__author__ = 'm_messiah'

AUTH_FORM = {
    'id': 'canvas',
    'rows': [
        {
            'view': "form",
            'id': "auth",
            'width': 350,
            'bottomPadding': 18,
            'elements': [
                {
                    'view': 'text',
                    'label': "Username",
                    'name': "user",
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
                    'cols': [
                        {
                            'view': 'button',
                            'label': "Login",
                            'click': 'submit',
                            'type': 'iconButton',
                            'icon': 'sign-in',
                            'align': 'center',
                            'css': "button_success",
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

ERROR_MESSAGE = {'type': "error"}
MESSAGE = {'type': 'default'}

PROFILES = {
    'id': 'canvas',
    'rows': [
        {
            'view': "dataview",
            'height': 800,
            'type': {
                'templateStart': "<div class='bg_panel card' data-uid='#uid#'>",
                'template': "<img class='cardImage' src='/userpics/#userpic#.jpg' />"
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
                            'height': 170,
                            'template': "<img src='/userpics/#userpic#.jpg' />"
                        },
                        {
                            "template": "<span class='webix_icon #icon# "
                                        "text_danger danger_icon'></span>"
                        }
                    ]
                },
                {
                    'template': """
                    <div class='profile'>
                        <h2>#name# #lastname#</h2>
                        <dl class="profile_info">
                            <dt>Birth</dt><dd>#birthdate#</dd>
                            <dt>Mobile</dt><dd>#mobile#</dd>
                            <dt>City</dt><dd>#city#</dd>
                            <dt>Marital status</dt><dd><span class="webix_icon #marital_icon#"></span></dd>
                        </dl>
                        <h3>Crimes</h3>
                        <dl class="crimes_list">
                            #crimes#
                        </dl>
                    </div>
                    """
                }
            ]
        }
    ],
}
