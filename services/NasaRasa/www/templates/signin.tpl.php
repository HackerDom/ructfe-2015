{extends 'page.tpl.php'}

{block 'title'}Sign in{/block}

{block 'content'}
    <form method="POST" action="/signin.php">
        Login <input type="text" name="login" /> <br />
        Password <input type="password" name="password" /> <br />
        <input type="submit" value="Sign in" />
        {if $result}
            <div>
                {$result}
            </div>
        {/if}
   </form>
{/block}