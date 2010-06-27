
<style>

#triggers img {
    border:0;
    cursor:pointer;
    margin-left:11px;
}
</style>
<table id="items">
    <thead>
        <tr><th></th><th>Name</th><th>Protocol</th><th>Ports</th></tr>
    </thead>
% for network in networks:
    <tr>
    <td class="hea">
        <img src="/static/delete.png" title="Delete network" class="delete">
    </td>
    % for item in network:
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
    $('img.delete').click(function() {
        td = this.parentElement.parentElement;
        name = td.children[1].innerText;
        $.post("networks", { action: 'delete', name: name},
            function(data){
                $(td).remove();
                $('.tooltip').hide();
            });
    });
});

</script>

