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
            {
                $result = $this->insert($table_name, $fields);
                if ($result)
                    $result = $this->conn->insert_id;
            }
            $this->conn->commit();

            return $result;
        }

        public function drop($table_name)
        {
            $query = 'DROP TABLE ' . $this->escape_field_name($table_name);
            return $this->query($query);
        }
    }

    class DbModel
    {
        static $connection;
        static $existing_tables = [];

        /* TODO: make own primary_key for each child of DbModel */
        static $primary_key = NULL;

        private $fields;

        function __construct($init_fields=[])
        {
            self::ensure_table_exists();

            $this->init_fields($init_fields);
        }

        /* TODO: cache results? */
        public static function build_schema($schema)
        {
            $primary_key = self::get_defined_primary_key();
            if ($primary_key !== NULL && ! array_key_exists($primary_key, $schema))
            {
                warning('Database model ' . get_called_class() . ': can\'t find primary key `' . $primary_key . '` in schema');
                $primary_key = NULL;
            }
            if ($primary_key === NULL)
            {
                $primary_key = 'id';
                if (! array_key_exists($primary_key, $schema))
                    $schema[$primary_key] = new DbIntField(['primary_key' => true, 'auto_increment' => true]);
            }

            return $schema;
        }

        private function init_fields($fields)
        {
            foreach ($fields as $field_name => $field_value)
                $this->$field_name = $field_value;
        }

        public static function get_table_name()
        {
            $class = get_called_class();
            return $class::$table_name;
        }

        public static function get_schema()
        {
            $class = get_called_class();
            return $class::get_schema();
        }

        public static function get_defined_primary_key()
        {
            $class = get_called_class();
            return $class::$primary_key;
        }

        public static function get_primary_key()
        {
            $primary_key = self::get_defined_primary_key();
            if ($primary_key === NULL)
                $primary_key = 'id';
            return $primary_key;
        }

        public static function ensure_table_exists()
        {
            $table_name = self::get_table_name();
            $schema = self::get_schema();

            if (in_array($table_name, self::$existing_tables))
                return;

            debug('DbModel::ensure_table_exists(' . $table_name . ')');

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
            $object = new $class();
            $object->fields = $db_row;

            $schema = self::get_schema();
            foreach ($object->fields as $field_name => &$field_value)
                $field_value = $schema[$field_name]->modify_on_get($field_value);

            return $object;
        }

        public static function find($filters, $limit=0)
        {
            if (array_key_exists('__pk__', $filters))
            {
                $filters[self::get_primary_key()] = $filters['__pk__'];
                unset($filters['__pk__']);
            }
            debug('DbModel::find(' . var_export($filters, true) . ')');
            self::ensure_table_exists();

            self::modify_fields_for_setting($filters);

            return self::load_objects(self::$connection->select(self::get_table_name(), $filters, $limit));
        }

        public static function find_one($filters)
        {
            $result = self::find($filters, 1);
            if (count($result) == 0)
                return NULL;
            return $result[0];
        }

        public static function objects()
        {
            return self::find([]);
        }

        public static function count($filters=[])
        {
            /* TODO: Optimize to SELECT COUNT(*) */
            return count(self::find($filters));
        }

        public function save()
        {
            debug('DbModel::save()');
            $fields_without_pk = $this->fields;
            unset($fields_without_pk[self::get_primary_key()]);

            $primary_key_value = array_key_exists(self::get_primary_key(), $this->fields) ? 
                                    $this->fields[self::get_primary_key()] :
                                    NULL;

            if (! $this->check_unique_constraints($fields_without_pk, $primary_key_value))
            {
                throw new DbConstraintsException('Can\'t save object: duplicated unique field');
                return false;
            }

            self::modify_fields_for_setting($fields_without_pk);

            $result = self::$connection->insert_or_update(self::get_table_name(), $fields_without_pk, [self::get_primary_key() => $primary_key_value]);
            if (is_int($result))
                $this->fields[self::get_primary_key()] = $result;

            return $result;
        }

        private static function modify_fields_for_setting(&$fields)
        {
            $schema = self::get_schema();
            foreach ($fields as $field_name => &$field_value)
                $field_value = $schema[$field_name]->modify_on_set($field_value);
        }

        private function check_unique_constraints($fields_without_pk, $ignored_pk_value)
        {
            $objects = self::objects();
            $schema = self::get_schema();

            foreach ($objects as $object)
            {
                if ($object->__get(self::get_primary_key()) == $ignored_pk_value)
                    continue;
                /* TODO: optimize */
                foreach ($schema as $field_name => $field)
                {
                    if (! $field->is_unique)
                        continue;
                    if ($field_name == self::get_primary_key())
                        continue;
                    if ($object->$field_name == $fields_without_pk[$field_name])
                        return false;
                }
            }
            return true;
        }

        public function __get($field)
        {
            debug('DbModel::__get(' . $field . ')');
            if (array_key_exists($field, self::get_schema()))
                return $this->fields[$field];

            throw new DbException('Database model ' . get_called_class() . ': can\'t find field `' . $field . '` in the schema');
            return NULL;
        }

        public function __set($field, $value)
        {
            debug('DbModel::__set(' . $field . ', ' . var_export($value, true) . ')');
            $schema = self::get_schema();
            if (! array_key_exists($field, $schema))
            {
                throw new DbException('Database model ' . get_called_class() . ': can\'t find field `' . $field . '` in the schema');
            }
            if ($field == $this->get_primary_key())
            {
                throw new DbException('Can\'t assign a value to the primary key of the object');
            }
            if (! $schema[$field]->can_assign_value($value))
            {
                warning('Can\'t assign this value to ' . get_called_class() . '::' . $field . ':');
                html_var_dump($value);
                throw new InvalidValueException('Can\'t assign this value to ' . get_called_class() . '::' . $field . ':');
            }

            $this->fields[$field] = $value;
            return true;
        }
    }

    DbModel::$connection = new DbConnection();

    class DbException extends Exception
    {
    }

    class InvalidValueException extends DbException
    {
    }

    class DbConstraintsException extends DbException
    {
    }
?>