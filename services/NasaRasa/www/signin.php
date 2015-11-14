<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/SessionManager.php';


    $result = null;
    if (array_key_exists('login', $_POST) && array_key_exists('password', $_POST))
    {
        $login = $_POST['login'];
        $password = $_POST['password'];

        if (SessionManager::try_authenticate($login, $password))
            redirect('/');
        else
            $result = 'Bad :-(';            
    }

    render('signin', ['result' => $result]);

?>
