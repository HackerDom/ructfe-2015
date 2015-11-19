<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<title>{block 'title'}NASA RASA{/block} &bull; Turio &bull; RuCTFE 2015</title>
		<meta name="description" content="NASA RASA is a system for reporting about new planes">
		<meta name="keywords" content="Turio, RuCTFE, NASA, RASA" />
		<meta name="author" content="Hackerdom team, hackerdom.ru, Andrew Gein aka andgein">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link href='http://fonts.googleapis.com/css?family=Roboto:400,700,500' rel='stylesheet' type='text/css'>
		<link href='http://fonts.googleapis.com/css?family=Lato:300,400' rel='stylesheet' type='text/css'>
		<link rel="stylesheet" href="/static/inc/bootstrap/css/bootstrap.min.css">

		<link rel="stylesheet" href="/static/css/unika.min.css">
		<link rel="stylesheet" href="/static/css/turio.css">
    	<link rel="stylesheet" href="/static/css/nasarasa.css">
	</head>
    <body class="service-page" data-spy="scroll" data-target="#main-navbar">
		<div class="page-loader"></div>  <!-- Display loading image while page loads -->
		<div class="body">
			<header id="header" class="header-main">
				<nav id="main-navbar" class="navbar navbar-default navbar-fixed-top" role="navigation">
					<div class="container">
						<div class="navbar-header">
                            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse"></button>
						    <a class="navbar-brand main-page-link" href="/home">&larr;</a> 
    					    <a class="navbar-brand" href="/">NASA RASA</a>
						</div>

                        <div class="collapse navbar-collapse" id="bs-navbar-collapse">
                            <ul class="nav navbar-nav navbar-right">
                                <li><a href="/">Home</a></li>
                                <li><a href="/users">Users</a></li>
                            </ul>
                        </div>
					</div>
				</nav>
			</header>
    		<section class="main-block" data-stellar-background-ratio="0.5">
				<div class="container">
					<div class="caption">

                        <div class="row about">
                            <div class="col-sm-2 center-block">
                                <a href="/">
                                    <img src="/static/logos/nasarasa.png" class="logo img-responsive">
                                </a>
                            </div>
                            <div class="col-sm-10">
                                <h1>NASA RASA</h1>

                                {block 'content'}
                                {/block}

                            </div>
                        </div>

					</div>
				</div>
            </section>
		</div>
		<script src="/static/inc/jquery/jquery-1.11.1.min.js"></script>
		<script src="/static/inc/bootstrap/js/bootstrap.min.js"></script>

		<script src="/static/js/theme.js"></script>
    </body>
</html>