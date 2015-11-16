<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/SessionManager.php';

    $result = null;
    if ($form = is_form_submitted(['login', 'password']))
    {
        if (SessionManager::try_authenticate($form['login'], $form['password']))
            redirect('/');
        else
            $result = 'Bad :-(';            
    }

    render('signin', ['result' => $result]);
?>