<?php
    require_once 'inc/shortcuts.php';
    require_once 'inc/db.php';
    require_once 'models/UserManager.php';
    require_once 'models/SessionManager.php';

    $result = null;
    if ($options = is_form_submitted(['login', 'password', 'first_name', 'last_name']))
    {
        try
        {
            if (UserManager::create_user($options['login'], $options['password'], $options['first_name'], $options['last_name']) &&
                SessionManager::try_authenticate($options['login'], $options['password']))
                redirect('/');
            else
                $result = 'Bad :-(';
        }
        catch (DbException $e)
        {
            $result = $e->getMessage();
        }
    }

    render('signup', ['result' => $result]);
?>