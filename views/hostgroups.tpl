
<style>

#triggers img {
    border:0;
    cursor:pointer;
    margin-left:11px;
}
</style>

<table id="items">
% for hostgroup in hostgroups:
    <tr>
    <td class="hea">
        <img src="/static/delete.png" title="Delete host group" class="delete">
    </td>
    % for item in hostgroup:
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
        $.post("hostgroups", { action: 'delete', name: name},
            function(data){
                $(td).remove();
                $('.tooltip').hide();
            });
    });
});

</script>

