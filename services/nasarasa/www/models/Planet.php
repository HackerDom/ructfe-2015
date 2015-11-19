<?php
    require_once 'inc/db.php';
    require_once 'models/User.php';

    class Planet extends DbModel
    {
        public static $table_name = 'planets';

        public static function get_schema()
        {
            return self::build_schema(['declination' => new DbDoubleField(['min_value' => -90, 'max_value' => 90]),
                                       'hour_angle' => new DbDoubleField(['min_value' => -12, 'max_value' => 12]),
                                       'brightness' => new DbDoubleField(['min_value' => 0, 'max_value' => 100]),
                                       'size' => new DbDoubleField(['min_value' => 0, 'max_field' => 100]),
                                       'color' => new DbCharField(['max_length' => 200]),
                                       'message' => new DbCharField(['max_length' => 1000]),
                                       'added_by' => new DbForeignField(['to' => 'User']),
                                       'added_at' => new DbTimeField(['init_with_current_timestamp' => true]),
                                       ]);
        }
    }
?>