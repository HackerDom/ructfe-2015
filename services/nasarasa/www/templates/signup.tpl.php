{extends 'page.tpl.php'}

{block 'title'}Sign up{/block}

{block 'content'}
    <h3>Sign up</h3>

    <div class="well">
        Welcome to NASA RASA! Please specify some information about you
    </div>

    <form method="POST" action="">
        <div class="form-group">
            <label>First name</label>
            <input type="text" class="form-control" placeholder="John" name="first_name" />
        </div>
        <div class="form-group">
            <label>Last name</label>
            <input type="text" class="form-control" placeholder="Johnson" name="last_name" />
        </div>
        <div class="form-group">
            <label>Login</label>
            <input type="text" class="form-control" placeholder="Login" name="login" />
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" class="form-control" placeholder="Password" name="password" />
        </div>
        <button type="submit" class="btn btn-default">Sign up</button>
        {if $result}
            <div class="alert alert-danger">
                {$result}
            </div>
        {/if}
   </form>
{/block}
