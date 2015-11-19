{extends 'page.tpl.php'}

{block 'title'}Error{/block}

{block 'content'}
    <div class="alert alert-danger">
        {$error}
    </div>
{/block}
