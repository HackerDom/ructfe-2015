<?php
    require_once 'vendor/autoload.php';

    $TEMPLATES_DIR = 'templates';
    $COMPILED_TEMPLATES_DIR = 'templates/compiled';

    if (! file_exists($COMPILED_TEMPLATES_DIR))
        mkdir($COMPILED_TEMPLATES_DIR, 0777, true);
    $fenom = Fenom::factory($TEMPLATES_DIR, $COMPILED_TEMPLATES_DIR, Fenom::FORCE_COMPILE | Fenom::AUTO_ESCAPE);

    function render($template, $vars)
    {        
        global $fenom;

        $fenom->display($template . '.tpl.php', $vars);
    }

    function redirect($url)
    {
        $url = str_replace('\n', '', $url);
        $url = str_replace('\r', '', $url);
        header('Location: ' . $url);

        exit;
    }

    function is_form_submitted($options)
    {
        $all = true;
        foreach ($options as $option)
            $all &= array_key_exists($option, $_POST);

        if (! $all)
            return false;

        $result = [];

        foreach ($options as $option)
            $result[$option] = $_POST[$option];

        return $result;
    }

    function http_error($code)
    {
        http_response_code($code);
        echo '<h1>Error ' . $code . '</h1>';
        exit;
    }
?>