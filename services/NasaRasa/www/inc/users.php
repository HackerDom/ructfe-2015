<?php
    require_once __DIR__ . '/db.php';

    class User extends DbModel
    {
        function __construct()
        {
            parent::__construct('users', ['id' => new DbIntField(), 'login' => new DbCharField(250), 'password' => new DbCharField(32)]);
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