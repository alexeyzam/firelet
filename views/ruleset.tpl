
<style>
img#help { float: right; }
div#help_ovr {
    background-color:#fff;
    display:none;
    width: 70em;
    padding:15px;
    text-align:left;
    border:2px solid #333;
    opacity:0.98;
    -moz-border-radius:6px;
    -webkit-border-radius:6px;
    -moz-box-shadow: 0 0 50px #ccc;
    -webkit-box-shadow: 0 0 50px #ccc;
}
#triggers img {
    border:0;
    cursor:pointer;
    margin-left:11px;
}
</style>

<img id="help" src="static/help.png" rel="div#help_ovr" title="Help">
<div id="help_ovr">
    <h4>Contextual help: Manage</h4>
    <p>TODO</p>
    <p>Here some nice Lorem ipsum:</p>
    <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
    <br/>
    <p>Press ESC to close this window</p>
</div>

<table id="items">
    <thead>
        <tr>
            <th></th><th>Enabled</th><th>Name</th><th>Source</th><th>Src service</th>
            <th>Destination</th><th>Dst service</th><th>Action</th><th>Log</th><th>Description</th>
        </tr>
    </thead>
    % for rid, rule in rules:
    <tr id="{{rid}}">
        <td class="hea">
            <img class="action" src="/static/new_above.png" title="New rule above" action="newabove">
            <img class="action" src="/static/new_below.png" title="New rule below" action="newbelow">
            <img class="action" src="/static/move_up.png" title="Move rule up" action="moveup">
            <img class="action" src="/static/move_down.png" title="Move rule down" action="movedown">
            %if rule[0] == "y":
            <img class="action" src="/static/disable.png" title="Disable rule" action="disable">
            %elif rule[0] == "n":
            <img class="action" src="/static/enable.png" title="Enable rule" action="enable">
            %end
            <img class="action" src="/static/delete.png" title="Delete rule" action="delete">
        </td>
        % for item in rule:
        <td>{{item}}</td>
        % end
    </tr>
    % end
</table>


<script>
$(function() {

    $("table#items tr td img[title]").tooltip({
        tip: '.tooltip',
        effect: 'fade',
        fadeOutSpeed: 100,
        predelay: 800,
        position: "bottom right",
        offset: [15, 15]
    });

    $("table#items tr td img").fadeTo("fast", 0.6);

    $("table#items tr td img").hover(function() {
      $(this).fadeTo("fast", 1);
    }, function() {
      $(this).fadeTo("fast", 0.6);
    });

    $(function() {
        $('img.action').click(function() {
            td = this.parentElement.parentElement;
            name = td.children[1].innerText;
            action = $(this).attr('action');
            $('.tooltip').hide();
            $.post("ruleset", { action: action, name: name, rid: td.id},
                function(data){
                    $('div.tabpane div').load('/ruleset');
                });
        });
    });
    // Help overlay
    $("img#help[rel]").overlay({ mask: {loadSpeed: 200, opacity: 0.9, }, });
});
</script>

