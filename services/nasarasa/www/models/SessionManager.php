<?php
    require_once __DIR__ . '/UserManager.php';

    class SessionManager
    {
        public static function init()
        {
            session_start();
            if (! array_key_exists('auth', $_SESSION))
                $_SESSION['auth'] = false;
        }

        public static function is_authenticated()
        {
            return $_SESSION['auth'];
        }

        public static function try_authenticate($login, $password)
        {
            if (UserManager::check_login_and_password($login, $password))
            {
                $_SESSION['auth'] = true;
                $_SESSION['login'] = $login;
                return true;
            }
            return false;
        }

        public static function logout()
        {
            $_SESSION['auth'] = false;
            unset($_SESSION['login']);
        }

        public static function current_user()
        {
            if ($_SESSION['auth'])
                return UserManager::get_user_by_login($_SESSION['login']);
            return false;
        }
    }

    SessionManager::init();

    class SessionException extends Exception
    {
    }
?>