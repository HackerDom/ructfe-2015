<?php
    require_once __DIR__ . '/db_fields.php';

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
            print '<b>DEBUG</b> [database query] "'.htmlspecialchars($query).'" <br>';

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
        private $table;
        private $schema;
        private $fields;
        private $primary_key;

        function __construct($table, $schema)
        {
            $this->table = $table;
            $this->schema = $schema;
            /* TODO */
            $this->primary_key = 'id';
        }

        private function load_objects($db_result)
        {
            $objects = [];
            while ($db_row = $db_result->fetch_assoc())
                $objects[] = $this->load_object($db_row);

            $db_result->free();
            return $objects;
        }

        private function load_object($db_row)
        {
            $class = get_class($this);

            $object = new $class;
            $object->fields = $db_row;

            return $object;
        }

        public function find($filters)
        {
            return $this->load_objects(self::$connection->select($this->table, $filters));
        }

        public static function objects()
        {
            $class = get_called_class();
            return (new $class)->find([]);
        }

        public function save()
        {
            $fields_without_pk = $this->fields;
            unset($fields_without_pk[$this->primary_key]);

            $primary_key_value = array_key_exists($this->primary_key, $this->fields) ? 
                                    $this->fields[$this->primary_key] :
                                    NULL;

            return self::$connection->insert_or_update($this->table, $fields_without_pk, [$this->primary_key => $primary_key_value]);
        }

        public function __get($field)
        {
            /* TODO: check if exists in schema */
            return $this->fields[$field];
        }

        public function __set($field, $value)
        {
            $this->fields[$field] = $value;
        }
    }

    DbModel::$connection = new DbConnection();
?>