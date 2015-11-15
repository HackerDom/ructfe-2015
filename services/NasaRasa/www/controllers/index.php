<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/SessionManager.php';

    $result = false;
    if (array_key_exists('result', $_GET))
        $result = $_GET['result'];

    render('index', ['authenticated' => SessionManager::is_authenticated(),
                     'result' => $result,
                     'current_user' => SessionManager::current_user()]);
?>