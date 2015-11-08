<?php
    // error_reporting(~E_ALL);

    require_once 'inc/users.php';
    require_once 'inc/logging.php';

    html_var_dump(count(User::objects()));
    print '<br>';

    $user = User::objects()[0];
    $user->login = 'test_changed' . rand(1, 1000);    
    $user->save();

    User::create('new_user', 'new_password');
    html_var_dump(count(User::objects()));

    html_var_dump(User::find(['login' => $user->login]));
?>