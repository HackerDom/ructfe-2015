<?php
    require_once 'inc/shortcuts.php';
    require_once 'inc/db.php';
    require_once 'inc/routing.php';
    require_once 'models/Planet.php';
    require_once 'models/SessionManager.php';

    $result = null;
    if (SessionManager::is_authenticated() && ($options = is_form_submitted(['declination', 'hour_angle', 'brightness', 'size', 'color'])))
    {
        try
        {   
            $planet = new Planet(['declination' => (int) $options['declination'],
                                  'hour_angle' => (int) $options['hour_angle'],
                                  'brightness' => (int) $options['brightness'],
                                  'size' => (int) $options['size'],
                                  'color' => $options['color'],
                                  'added_by' => SessionManager::current_user()]);
            $planet->save();
            redirect('/?planet_added=1');
        }
        catch (DbException $e)
        {
            $result = $e->getMessage();
        }
    }

    $index = new Controller('index', ['result' => $result]);
    $index->run();
?>