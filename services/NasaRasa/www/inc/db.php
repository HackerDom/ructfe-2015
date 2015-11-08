<?php
    require_once __DIR__ . '/db_fields.php';
    require_once __DIR__ . '/logging.php';

    class DbConnection
    {
        private $conn;

        function __construct()
        {
            /* TODO */
            $DB_HOST = '127.0.0.1';
            $DB_USER = 'nasarasa';
            $DB_PASS = '2ueOVgi6CCRJh8hbA5PR';
            $DB_NAME = 'nasarasa';

            $this->conn = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
            if ($this->conn->connect_error)
                /* TODO */
                die('Connection error, code ' . $this->conn->connect_errno . ': '. $this->conn->connect_error);
        }

        function __destruct()
        {
            $this->conn->close();
        }

        private function escape_field_name($field_name)
        {
            return '`' . $this->conn->real_escape_string($field_name) . '`';
        }

        private function escape_field_value($field_value)
        {
            if ($field_value == NULL)
                return 'NULL';

            return '"' . $this->conn->real_escape_string($field_value) . '"';
        }

        private function query($query)
        {
            debug('Database query "' . $query . '"');

            $result = $this->conn->query($query);
            if ($result === false)
                die('Database query error: ' . $this->conn->error);

            return $result;
        }

        private function build_where_by_filter($filters)
        {
            $where = [];
            foreach ($filters as $filter_key => $filter_value)
                $where[] = $this->escape_field_name($filter_key) . ' = ' . $this->escape_field_value($filter_value);

            $where = join(' AND ', $where);
            return $where;
        }

        private function build_set_statement($fields)
        {
            $statement = '';
            if (count($fields) > 0)
            {
                $statement .= ' SET ';

                $assigns = [];
                foreach ($fields as $field_name => $field_value)
                    $assigns[] = $this->escape_field_name($field_name) . ' = ' . $this->escape_field_value($field_value);
                $statement .= join(', ', $assigns);
            }

            return $statement;        
        }

        public function create_table($table_name, $schema)
        {
            $statement = 'CREATE TABLE IF NOT EXISTS ' . $this->escape_field_name($table_name) . ' (';

            $columns = [];
            foreach ($schema as $field_name => $field)
                $columns[] = $this->escape_field_name($field_name) . ' ' . $field->get_type_definition();

            $statement .= join(', ', $columns);
            $statement .= ')';

            return $this->query($statement);
        }

        public function select($table_name, $filters, $limit=0)
        {
            $where = $this->build_where_by_filter($filters);

            $query = 'SELECT * FROM ' . $this->escape_field_name($table_name);
            
            if (strlen($where) > 0)
                $query .= ' WHERE ' . $where;

            if ($limit != 0)
                $query .= ' LIMIT ' . (int) $limit;

            return $this->query($query);
        }

        public function insert($table_name, $fields)
        {
            $query = 'INSERT INTO ' . $this->escape_field_name($table_name);
            $query .= $this->build_set_statement($fields);

            return $this->query($query);
        }

        public function update($table_name, $fields, $filters)
        {
            $query = 'UPDATE ' . $this->escape_field_name($table_name);

            $query .= $this->build_set_statement($fields);

            $where = $this->build_where_by_filter($filters);
            if (strlen($where) > 0)
                $query .= ' WHERE ' . $where;

            return $this->query($query);
        }

        public function insert_or_update($table_name, $fields, $filters)
        {            
            $this->conn->begin_transaction();
            if ($this->select($table_name, $filters, 1)->num_rows > 0)
                $result = $this->update($table_name, $fields, $filters);
            else
                $result = $this->insert($table_name, $fields);
            $this->conn->commit();

            return $result;
        }
    }

    class DbModel
    {
        static $connection;
        static $existing_tables = [];

        public static $table;
        public static $schema;
        private static $primary_key;

        private $fields;

        function __construct($init_fields=[])
        {
            self::ensure_table_exists();

            $this->init_fields($init_fields);
        }

        public static function init_model()
        {
            if (self::$primary_key !== NULL && ! array_key_exists(self::$primary_key, self::get_schema()))
            {
                warning('Database model ' . $class . ': can\'t find primary key `' . self::$primary_key . '` in schema');
                self::$primary_key = NULL;
            }
            if (self::$primary_key == NULL)
            {
                self::$primary_key = 'id';
                if (! array_key_exists(self::$primary_key, self::get_schema()))
                    self::get_schema()[self::$primary_key] = new DbIntField(['primary_key' => true, 'auto_increment' => true]);
            }
        }

        private function init_fields($fields)
        {
            foreach ($fields as $field_name => $field_value)
                $this->$field_name = $field_value;
        }

        public static function get_table_name()
        {
            $class = get_called_class();
            return $class::$table;            
        }

        public static function &get_schema()
        {
            $class = get_called_class();
            return $class::$schema;            
        }

        public static function ensure_table_exists()
        {
            $table_name = self::get_table_name();
            $schema = self::get_schema();

            if (in_array($table_name, self::$existing_tables))
                return;

            self::$existing_tables[] = $table_name;

            return self::$connection->create_table($table_name, $schema);
        }

        private static function load_objects($db_result)
        {
            $objects = [];
            while ($db_row = $db_result->fetch_assoc())
                $objects[] = self::load_object($db_row);

            $db_result->free();
            return $objects;
        }

        private static function load_object($db_row)
        {
            $class = get_called_class();
            $object = new $class;
            $object->fields = $db_row;

            return $object;
        }

        public static function find($filters)
        {
            self::ensure_table_exists();
            return self::load_objects(self::$connection->select(self::get_table_name(), $filters));
        }

        public static function objects()
        {
            return self::find([]);
        }

        public function save()
        {
            debug('DbModel::save()');
            $fields_without_pk = $this->fields;
            unset($fields_without_pk[self::$primary_key]);

            $primary_key_value = array_key_exists(self::$primary_key, $this->fields) ? 
                                    $this->fields[self::$primary_key] :
                                    NULL;

            return self::$connection->insert_or_update(self::get_table_name(), $fields_without_pk, [self::$primary_key => $primary_key_value]);
        }

        public function __get($field)
        {
            debug('DbModel::__get(' . $field . ')');
            if (array_key_exists($field, self::get_schema()))
                return $this->fields[$field];

            warning('Database model ' . get_called_class() . ': can\'t find field `' . $field . '` in the schema');
            return NULL;
        }

        public function __set($field, $value)
        {
            debug('DbModel::__set(' . $field . ', ' . $value . ')');
            if (! array_key_exists($field, self::get_schema()))
            {
                warning('Database model ' . get_called_class() . ': can\'t find field `' . $field . '` in the schema');
                return;
            }
            $this->fields[$field] = $value;
        }
    }

    DbModel::$connection = new DbConnection();
?>