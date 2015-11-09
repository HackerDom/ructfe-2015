<?php
    require_once 'inc/db.php';

    class Post extends DbModel
    {
        public static $table_name = 'posts';

        public static function get_schema()
        {
            return self::build_schema(['title' => new DbCharField(['max_length' => 100]), 'text' => new DbCharField(['max_length' => 1000])]);
        }
    }
?>