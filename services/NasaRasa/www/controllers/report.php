<?php
    require_once 'inc/shortcuts.php';
    require_once 'inc/db.php';
    require_once 'inc/routing.php';
    require_once 'models/Planet.php';
    require_once 'models/SessionManager.php';

    $result = null;
    if (SessionManager::is_authenticated() && ($form = is_form_submitted(['declination', 'hour_angle', 'brightness', 'size', 'color', 'message'])))
    {
        try
        {   
            $planet = new Planet(['declination' => (int) $form['declination'],
                                  'hour_angle' => (int) $form['hour_angle'],
                                  'brightness' => (int) $form['brightness'],
                                  'size' => (int) $form['size'],
                                  'color' => $form['color'],
                                  'message' => $form['message'],
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