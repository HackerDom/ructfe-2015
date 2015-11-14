<?php
    require_once __DIR__ . '/db.php';
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

        public function can_assign_value($value)
        {
            return true;
        }

        public function modify_on_set($value)
        {
            return $value;
        }

        public function modify_on_get($value)
        {
            return $value;
        }
    }

    class DbIntField extends DbField
    {
        private $is_auto_increment = false;
        private $min_value = null;
        private $max_value = null;

        function __construct($options=[])
        {
            parent::__construct($options);

            if (array_key_exists('auto_increment', $options))
                $this->is_auto_increment = (bool) $options['auto_increment'];

            if (array_key_exists('min_value', $options))
                $this->min_value = (int) $options['min_value'];

            if (array_key_exists('max_value', $options))
                $this->max_value = (int) $options['max_value'];

            $this->type_definition = 'INT' . ($this->is_auto_increment ? ' AUTO_INCREMENT' : '');
        }

        public function can_assign_value($value)
        {
            if (! parent::can_assign_value($value))
                return false;
                
            if (! is_int($value))
                throw new DbConstraintsException('Value must be integer');

            if ($this->min_value != null && $value < $this->min_value)
                throw new DbConstraintsException('Value must be not less than ' . $this->min_value);
            if ($this->max_value != null && $value > $this->max_value)
                throw new DbConstraintsException('Value must be not more than ' . $this->max_value);

            return true;
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

    class DbForeignField extends DbField
    {
        private $class;

        function __construct($options=[])
        {
            parent::__construct($options);

            if (! array_key_exists('to', $options))
                throw new DbException('You should define `to` option for foreign key');
 
            $this->class = (string) $options['to'];
            try
            {
                $obj = new $this->class;
            }
            catch (Exception $e)
            {
                throw new DbException('Can\'t find model for foreign key: ' . $this->class);
            }
            if (! is_subclass_of($this->class, 'DbModel'))
                throw new DbException('Foreign key\'s model (' . $this->class . ') should extend DbModel');

            $this->type_definition = 'INT';
        }

        public function can_assign_value($value)
        {
            if (get_class($value) != $this->class)
                throw new InvalidValidException('This field must be ' . $this->class . ' type');
            return true;
        }

        public function modify_on_set($value)
        {
            debug('ForeignKey(' . $this->class . ')::modify_on_set(' . var_export($value, true) . ')');
            $pk = $value->get_primary_key();
            return $value->$pk;
        }

        public function modify_on_get($value)
        {
            $class = $this->class;
            return $class::find_one(['__pk__' => $value]);
        }
    }
?>