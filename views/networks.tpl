
<style>

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
        <tr><th></th><th>Name</th><th>Network</th><th>Netmask</th></tr>
    </thead>
% for rid, network in networks:
    <tr id="{{rid}}">
    <td class="hea">
        <img src="/static/delete.png" title="Delete network" class="delete">
    </td>
    % for item in network:
    <td>{{item}}</td>
    % end
    </tr>
% end
</table>


<style>
img#help {
    float: right;
}
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
</style>


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
        $('img.delete').click(function() {
            td = this.parentElement.parentElement;
            $.post("networks", { action: 'delete', rid: td.id},
                function(data){
                    $('div.tabpane div').load('/networks');
                });
        });
    });

    // Help overlay
    $("img#help[rel]").overlay({ mask: {loadSpeed: 200, opacity: 0.9, }, });
});
</script>


