{extends 'page.tpl.php'}

{block 'title'}NASA RASA{/block}

{block 'content'}
    <div class="well">
        {if $authenticated}
            <div>You're logged in as <b><a href="/users/{$current_user->id}">{$current_user->login}</a></b> (<a href="/logout">logout</a>)</div>
        {/if}
        <div>Report us information about unknown planet and it'll be named after you.</div>
    </div>

    <div class="col-sm-8">
        {if $authenticated}
            {include 'report-form.tpl.php'}
        {else}
            <div class="row">
                <a class="btn btn-default" href="/signup" role="button">Sign up</a>
                <a class="btn btn-default" href="/signin" role="button">Sign in</a>
            </div>
        {/if}
    </div>
{/block}
