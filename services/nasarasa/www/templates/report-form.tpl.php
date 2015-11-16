<h3>Let us know about unknown planet</h3>

<form action="/report" method="POST">
    {if $result}
        <div class="alert alert-danger">
            {$result}
        </div>
    {/if}
    {if $.get['planet_added']}
        <div class="alert alert-success">
            Information has been successfully added, thank you! You can see it on your <a href="/users/{$current_user->id}">personal page</a>.
        </div>
    {/if}
    <div class="form-group">
        <label>Declination (from -90 to 90 degrees)</label>
        <input type="text" class="form-control" name="declination" />
    </div>
    <div class="form-group">
        <label>Hour angle (from -12 to 12 degrees)</label>
        <input type="text" class="form-control" name="hour_angle" />
    </div>
    <div class="form-group">
        <label>Brightness (from 0 to 100)</label>
        <input type="text" class="form-control" name="brightness" />
    </div>
    <div class="form-group">
        <label>Size (from 0 to 100)</label>
        <input type="text" class="form-control" name="size" />
    </div>
    <div class="form-group">
        <label>Color</label>
        <input type="text" class="form-control" name="color" />
    </div>
    <div class="form-group">
        <label>Message</label>
        <textarea class="form-control" placeholder="Any message which will be visible only for you and site administrators" name="message"></textarea>
    </div>
    <button class="btn btn-default">Report</button>
</form>