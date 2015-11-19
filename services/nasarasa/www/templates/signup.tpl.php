{extends 'page.tpl.php'}

{block 'title'}Sign up{/block}

{block 'content'}
    <h3>Sign up</h3>

    <div class="well">
        Welcome to NASA RASA! Please specify some information about you
    </div>

    <form method="POST" action="">
        <div class="form-group">
            <input type="text" class="form-control" placeholder="First Name" name="first_name" />
        </div>
        <div class="form-group">
            <input type="text" class="form-control" placeholder="Last Name" name="last_name" />
        </div>
        <div class="form-group">
            <input type="text" class="form-control" placeholder="Login" name="login" />
        </div>
        <div class="form-group">
            <input type="password" class="form-control" placeholder="Password" name="password" />
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-default">Sign up</button>
        </div>
        {if $result}
            <div class="alert alert-danger">
                {$result}
            </div>
        {/if}
   </form>
{/block}
