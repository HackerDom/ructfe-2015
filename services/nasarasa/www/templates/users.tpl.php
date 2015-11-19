{extends 'page.tpl.php'}

{block 'title'}Users{/block}

{block 'content'}
    <h3>Last registered users</h3>
    <div class="last-users">
        {foreach $last_users as $user index=$index}
            <div class="user">
                <div class="number">
                    {$index+1}.
                </div>
                <div class="">
                    <a href="/users/{$user->id}">
                        {if ($user->first_name|length == 0) && ($user->last_name|length == 0)}
                            Unknown name
                        {else}
                            {$user->first_name} {$user->last_name}
                        {/if}
                    </a>
                </div>
            </div>
        {foreachelse}
            No users yet. <a href="/signup">Be the first</a>!
        {/foreach}
    </div>
{/block}
