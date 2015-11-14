<?php
    // error_reporting(~E_ALL);

    require_once 'inc/logging.php';
    require_once 'models/User.php';
    require_once 'models/Planet.php';
    require_once 'models/UserManager.php';

    require_once 'inc/db.php';
    $db = new DbConnection();
    $db->drop('users');
    $db->drop('planets');

    try
    {
        html_var_dump(UserManager::create_user('new_user', 'new_password'));
        html_var_dump(UserManager::create_user('new_user', 'new_password2222'));
    }
    catch (DbException $e)
    {
        warning($e->getMessage());
    }

    html_var_dump(UserManager::check_login_and_password('new_user   ', 'new_password'));

    $user1 = UserManager::get_user_by_login('new_user');
    $user2 = UserManager::create_user('user2', 'password2');

    $planet = new Planet(['declination' => -50, 'hour_angle' => 10, 'brightness' => 40, 'size' => 50, 'color' => 'white', 'added_by' => $user1]);
    $planet->save();
    html_var_dump($planet);

    $planet2 = new Planet(['added_by'=> $user2]);
    $planet2->save();

    html_var_dump(Planet::count(['added_by' => $user1]));
    html_var_dump(Planet::count(['added_by' => $user2]));
    html_var_dump(Planet::count());
?>