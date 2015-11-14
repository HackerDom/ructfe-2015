<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/SessionManager.php';
    require_once 'models/User.php';

    $last_users = User::find(['__order_by__' => '-id'], 10);

    render('index', ['authenticated' => SessionManager::is_authenticated(),
                     'result' => false,
                     'current_user' => SessionMAnager::current_user(),
                     'last_users' => $last_users]);
?>
