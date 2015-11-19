<?php
    require_once 'inc/shortcuts.php';
    require_once 'inc/db.php';
    require_once 'models/UserManager.php';
    require_once 'models/SessionManager.php';

    $result = null;
    if ($form = is_form_submitted(['login', 'password', 'first_name', 'last_name']))
    {
        try
        {
            if (UserManager::create_user($form['login'], $form['password'], $form['first_name'], $form['last_name']) &&
                SessionManager::try_authenticate($form['login'], $form['password']))
                redirect('/');
            else
                $result = 'Bad :-(';
        }
        catch (DbException $e)
        {
            if ($e instanceof DbConstraintsException)
                $result = 'This login is already registered, please select another one';
            else
                $result = $e->getMessage();
        }
    }

    render('signup', ['result' => $result]);
?>