<?php
    require_once __DIR__ . '/db.php';

    class User extends DbModel
    {
        function __construct($init_fields=[])
        {
            parent::__construct($init_fields);
        }
    }

    User::$table = 'users';
    User::$schema = ['login' => new DbCharField(['max_length' => 250]), 'password' => new DbCharField(['max_length' => 32])];

?>