# coding=utf-8
__author__ = 'm_messiah'

AUTH_FORM = {
    'view': "form",
    'id': "auth",
    'width': 300,
    'elements': [
        {
            'view': 'text',
            'label': "Username",
            'name': "user",
        },
        {
            'view': 'text',
            'label': "Password",
            'name': "password",
            'type': 'password',
        },
        {
            'view': 'button',
            'label': "Login",
            'click': 'submit',
            'type': 'iconButton',
            'icon': 'sign-in',
            'align': 'center',
        },
    ]
}

FORM_ERROR = {'view': 'label'}

INDEX = {
    'id': 'output',
    'view': "dataview",
}