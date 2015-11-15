<?php
    require_once 'inc/shortcuts.php';
    require_once 'models/SessionManager.php';

    SessionManager::logout();

    redirect('/');
?>