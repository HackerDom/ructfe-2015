<?php
    class DbField
    {
        function __construct()
        {
        }
    }

    class DbIntField extends DbField
    {
    }

    class DbCharField extends DbField
    {
        function __construct($max_length)
        {
        }
    }
?>