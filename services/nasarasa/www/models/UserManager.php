<?php
    require_once __DIR__ . '/User.php';

    class UserManager
    {
        public static function create_user($login, $password, $first_name, $last_name)
        {
            $user = new User(['login' => $login, 'password' => $password, 'first_name' => $first_name, 'last_name' => $last_name]);
            $user->save();
            return $user;
        }

        public static function get_user_by_login($login)
        {
            $user = User::find_one(['login' => $login]);
            if (! $user)
                return false;
            return $user;
        }

        public static function check_login_and_password($login, $password)
        {
            return User::find_one(['login' => $login, 'password' => $password]) !== NULL;
        }
    }
?>