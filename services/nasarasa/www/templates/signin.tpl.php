{extends 'page.tpl.php'}

{block 'title'}Sign in{/block}

{block 'content'}
    <h3>Sign in</h3>

    <form method="POST" action="">
        {if $result}
            <div class="alert alert-danger">
                {$result}
            </div>
        {/if}

        <div class="form-group">
            <input type="text" class="form-control" placeholder="Login" name="login" />
        </div>
        <div class="form-group">
            <input type="password" class="form-control" placeholder="Password" name="password" />
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-default">Sign in</button>
        </div>
   </form>
{/block}
