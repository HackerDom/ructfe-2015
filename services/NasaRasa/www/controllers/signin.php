<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/SessionManager.php';

    $result = null;
    if ($options = is_form_submitted(['login', 'password']))
    {
        if (SessionManager::try_authenticate($options['login'], $options['password']))
            redirect('/');
        else
            $result = 'Bad :-(';            
    }

    render('signin', ['result' => $result]);
?>