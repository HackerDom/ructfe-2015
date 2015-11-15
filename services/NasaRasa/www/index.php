<?php
    require_once 'inc/routing.php';
    require_once 'inc/shortcuts.php';

    $url = $_SERVER['REQUEST_URI'];

    $controllers = ['/' => 'index',
                    '/users' => 'users',
                    '/users/:id' => 'users',
                    '/report' => 'report',
                    '/signin' => 'signin',
                    '/signup' => 'signup',
                    '/logout' => 'logout',
                    ];

    $routing = new Routing($controllers);
    $controller = $routing->find($url);
    if (! $controller)
        error(404);
    $controller->run();
?>