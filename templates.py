# coding=utf-8
__author__ = 'm_messiah'

AUTH_FORM = {
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

ERROR_MESSAGE = {'type': "error"}
MESSAGE = {'type': 'default'}

INDEX = {
    'id': 'output',
    'view': "dataview",
}