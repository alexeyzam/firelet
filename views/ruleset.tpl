
<style>

#triggers img {
    border:0;
    cursor:pointer;
    margin-left:11px;
}
</style>

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

</script>

