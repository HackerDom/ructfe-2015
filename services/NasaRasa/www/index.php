<?php
    // error_reporting(~E_ALL);

    require_once 'inc/logging.php';
    require_once 'models/users.php';
    require_once 'models/posts.php';


    html_var_dump(count(User::objects()));
    print '<br>';

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
?>