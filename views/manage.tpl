<button id="save" rel="#prompt"><img src="static/save.png"  title="Save"> Save</button>
<br/>
<button id="check" rel="#prompt"><img src="static/check.png"  title="Check"> Check</button>
<br/>
<button id="deploy" rel="#prompt"><img src="static/deploy.png"  title="Deploy"> Deploy</button>
<style>
div.css-panes div button {
    width: 6em;
    padding: 1px;
}
</style>

<script>
$(function() {
    $('button#save').click(function() {
        $.post("save",
            function(data){            });
    });
    $('button#check').click(function() {
        $.post("check",
            function(data){            });
    });
    $('button#deploy').click(function() {
        $.post("deploy",
            function(data){            });
    });
});
</script>
