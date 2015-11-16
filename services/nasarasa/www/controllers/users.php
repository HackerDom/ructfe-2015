<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/User.php';
    require_once 'models/Planet.php';
    require_once 'models/SessionManager.php';

    if (array_key_exists('id', $_GET))
    {
        $user_id = (int) $_GET['id'];
        $user = User::find_one(['__pk__' => $user_id]);
        if ($user)
        {
            $self = $user->id === SessionManager::current_user()->id;
            $planets = Planet::find(['added_by' => $user]);

            render('user', ['user' => $user, 'planets' => $planets, 'self' => $self]);
            exit;
        }
    }

    $last_users = User::find(['__order_by__' => '-id'], 10);
    render('users', ['last_users' => $last_users]);
?>