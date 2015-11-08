<?php
    require_once __DIR__ . '/logging.php';

    class DbField
    {
        private $is_primary_key = false;
        public $is_unique = false;

        protected $type_definition = 'UNKNOWN';
        
        function __construct($options=[])
        {
            if (array_key_exists('primary_key', $options))
                $this->is_primary_key = (bool) $options['primary_key'];
            if (array_key_exists('unique', $options))
                $this->is_unique = (bool) $options['unique'];
        }

        public function get_type_definition()
        {
            $type = $this->type_definition;
            if ($this->is_primary_key)
                $type .= ' PRIMARY KEY';
            return $type;
        }
    }

    class DbIntField extends DbField
    {
        private $is_auto_increment = false;

        function __construct($options=[])
        {
            parent::__construct($options);
            if (array_key_exists('auto_increment', $options))
                $this->is_auto_increment = (bool) $options['auto_increment'];

            $this->type_definition = 'INT' . ($this->is_auto_increment ? ' AUTO_INCREMENT' : '');
        }
    }

    class DbCharField extends DbField
    {
        const DEFAULT_MAX_LENGTH = 255;

        private $max_length = self::DEFAULT_MAX_LENGTH;

        function __construct($options=[])
        {
            parent::__construct($options);

            if (array_key_exists('max_length', $options))
                $this->max_length = (int) $options['max_length'];

            if ($this->max_length <= 0 || $this->max_length > 10000)
            {
                warning('Wrong max_length: ' . $this->max_length);
                $this->max_length = self::DEFAULT_MAX_LENGTH;
            }

            $this->type_definition = 'VARCHAR(' . $this->max_length . ')';
        }
    }
?>