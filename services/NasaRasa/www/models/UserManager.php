<?php
    require_once __DIR__ . '/User.php';

    class UserManager
    {
        public static function create_user($login, $password)
        {
            $user = new User(['login' => $login, 'password' => $password]);
            $user->save();
            return $user;
        }

        public static function get_user_by_login($login)
        {
            return User::find_one(['login' => $login]);
        }

        public static function check_login_and_password($login, $password)
        {
            return User::find_one(['login' => $login, 'password' => $password]) !== NULL;
        }
    }
?>