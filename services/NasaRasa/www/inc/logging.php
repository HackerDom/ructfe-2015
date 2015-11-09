<?php
    function warning($message)
    {
        print '<b>[WARNING]</b> ' . htmlspecialchars($message) . '<br>';
    }

    function debug($message)
    {
        print '<b>[DEBUG]</b> ' . htmlspecialchars($message) . '<br>';
    }

    function html_var_dump($var)
    {
        print '<pre>';
        ob_start();
        var_dump($var);
        $output = ob_get_contents();
        ob_end_clean();
        print htmlspecialchars($output, ENT_QUOTES);
        print '</pre>';
    }
?>