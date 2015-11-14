<?php
    require_once 'vendor/autoload.php';

    $TEMPLATES_DIR = 'templates';
    $COMPILED_TEMPLATES_DIR = 'templates/compiled';
    /* TODO: Create $COMPILED_TEMPLATES_DIR if not exists */
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

?>