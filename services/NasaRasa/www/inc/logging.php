<?php
    $DEBUG_MODE = false;

    function warning($message)
    {
        print '<b>[WARNING]</b> ' . htmlspecialchars($message) . '<br>';
    }

    function debug($message)
    {
        global $DEBUG_MODE;
        if ($DEBUG_MODE)
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

    function exception_handler($exception)
    {
        print '<div class="alert alert-danger">';
        print '<b>Fatal error</b>:  Uncaught exception \'' . htmlspecialchars(get_class($exception)) . '\' with message ';
        print $exception->getMessage() . '<br>';
        print 'Stack trace:<pre>' . htmlspecialchars($exception->getTraceAsString()) . '</pre>';
        print 'thrown in <b>' . htmlspecialchars($exception->getFile()) . '</b> on line <b>' . $exception->getLine() . '</b><br>';
        print '</div>';
     }
    set_exception_handler('exception_handler');
?>