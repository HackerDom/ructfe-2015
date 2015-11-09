<?php
    // error_reporting(~E_ALL);

    require_once 'inc/logging.php';
    require_once 'models/User.php';
    require_once 'models/Post.php';
    require_once 'inc/UserManager.php';

    /*
    html_var_dump(count(User::objects()));

    if (count(User::objects()) > 0)
    {
        $user = User::objects()[0];
        $user->login = 'test_changed' . rand(1, 1000);    
        $user->save();

        $created = true;
    }

    (new User(['login' => 'new_user', 'password' => 'new_password']))->save();
    html_var_dump(count(User::objects()));

    if (isset($created))
        html_var_dump(User::find(['login' => $user->login]));



    $post = new Post(['title' => 'New post!', 'text' => 'It\'s a text of a new post']);
    $post->save();

    html_var_dump(count(User::objects()));
    html_var_dump(count(Post::objects()));
    */

    html_var_dump(UserManager::create_user('new_user', 'new_password'));
    html_var_dump(UserManager::create_user('new_user', 'new_password2222'));
    html_var_dump(UserManager::check_login_and_password('new_user   ', 'new_password'));
?>