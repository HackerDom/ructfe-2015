<?php
    class Controller
    {
        public function __construct($name, $options=[])
        {
            $this->name = $name;
            $this->options = $options;
        }

        public function run()
        {
            global $fenom;

            foreach ($this->options as $key => $value)
                $_GET[$key] = $value;

            require 'controllers/' . $this->name . '.php';
        }
    }

    class Routing
    {
        private $routes;

        public function __construct($routes)
        {
            $this->routes = $routes;
        }

        private function satisfy($route, $url)
        {
            $route_parts = explode('/', $route);
            $url_parts = explode('/', $url);

            $options = [];

            if (count($route_parts) != count($url_parts))
                return false;

            for ($idx = 0; $idx < count($route_parts); $idx++)
            {
                $route_part = $route_parts[$idx];
                $url_part = $url_parts[$idx];
                if (strlen($route_part) > 0 && $route_part[0] == ':')
                {
                    if (! is_numeric($url_part))
                        return false;
                    $options[substr($route_part, 1)] = (int) $url_part;
                }
                else
                {
                    if ($route_part != $url_part)
                        return false;
                }
            }

            return $options;
        }

        public function find($url)
        {
            $pos = strpos($url, '?');
            if ($pos !== false)
                $url = substr($url, 0, $pos);

            foreach ($this->routes as $route_name => $route)
            {
                $options = $this->satisfy($route_name, $url);
                if ($options !== false)
                    return new Controller($route, $options);
            }
        }
    }

?>