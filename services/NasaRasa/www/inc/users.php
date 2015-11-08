<?php
    require_once __DIR__ . '/db.php';

    class User extends DbModel
    {
        function __construct()
        {
            $this->table = 'users';
            $this->schema = ['login' => new DbCharField(250), 'password' => new DbCharField(32)];

            call_user_func_array('parent::__construct', func_get_args());
        }

        public static function create($login, $password)
        {
           /* TODO initializing from constructor */
           $user = new User();
           $user->login = $login;
           $user->password = $password;
           $user->save();
        }
    }
?>