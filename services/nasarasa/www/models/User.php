<?php
    require_once 'inc/db.php';

    class User extends DbModel
    {
        public static $table_name = 'users';

        public static function get_schema()
        {
            return self::build_schema(['login' => new DbCharField(['max_length' => 250, 'unique' => true]),
                                       'password' => new DbCharField(['max_length' => 32]),
                                       'first_name' => new DbCharField(['max_length' => 200]),
                                       'last_name' => new DbCharField(['max_length' => 200]),
                                       'registered_at' => new DbTimeField(['init_with_current_timestamp' => true]),
                                      ]);
        }
    }
?>