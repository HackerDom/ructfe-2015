<?php
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