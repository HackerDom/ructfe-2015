<?php
    require_once __DIR__ . '/db.php';

    class User extends DbModel
    {
        function __construct($init_fields=[])
        {
            $this->table = 'users';
            $this->schema = ['login' => new DbCharField(250), 'password' => new DbCharField(32)];

            parent::__construct($init_fields);
        }
    }
?>