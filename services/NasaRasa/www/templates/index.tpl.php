{extends 'page.tpl.php'}

{block 'title'}NASA RASA{/block}

{block 'content'}
    <h1>
        Welcome to NASA RASA
    </h1>

    {if $authenticated}
        {include 'user.tpl.php' user=$current_user}
    {else}
        {include 'signin.tpl.php'}
    {/if}

    <div class="last-users">
        <h3>Last registered users</h3>
        {foreach $last_users as $user}
            <div class="user">
                <a href="/users/{$user->id}">{$user->login}</a>
            </div>
        {/foreach}
    </div>
{/block}