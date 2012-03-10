<img id="help" src="static/help.png" rel="div#help_ovr" title="Help">
<div id="help_ovr">
    <h4>Contextual help: Manage</h4>
    <p>TODO</p>
    <p>Here some nice Lorem ipsum:</p>
    <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
    <br/>
    <p>Press ESC to close this window</p>
</div>

<img id="rss" src="static/rss.png" rel="div#rss_ovr" title="RSS feeds">
<div id="rss_ovr">
    <h4>RSS Feeds</h4>
    <a href="rss/messages" class="feed">Messages</a> <br/>
    <a href="rss/confsaves" class="feed">Configuration save</a> <br/>
    <a href="rss/deployments" class="feed">Deployments</a> <br/>
    <a href="rss/deployments/" class="feed">Deployments on a host or hostgroup</a>
    <p>Press ESC to close this window</p>
</div>


<button id="save" rel="#savediag">
    <img id="save" src="static/save.png" title="Save"> Save
</button>
<br/>
<button id="check" rel="#prompt" rel="#check_ovr"><img id="check" src="static/check.png" rel="#check_ovr" title="Check"> Check</button>
<br/>
% if can_deploy:
<button id="deploy" rel="#prompt"><img src="static/deploy.png"  title="Deploy"> Deploy</button>
% end
<div id="version_list">
    <table>
    </table>
</div>

<!-- check_feedback overlay -->
<div class="ovl" id="check_ovr">
    <h2>Configuration check</h2>
    <div id="diff_table">
    </div>
    <br />
</div>

<!-- version diff overaly -->
<div class="ovl" id="version_diff_ovr">
    <h2>Version diff</h2>
    <div id="version_diff">
    </div>
    <br />
</div>

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

img#rss {
    float: right;
    padding: 4px;
}
div#rss_ovr {
    background-color:#fff;
    display:none;
    width: 30em;
    padding:15px;
    text-align:left;
    border:2px solid #333;
    opacity:0.98;
    -moz-border-radius:6px;
    -webkit-border-radius:6px;
    -moz-box-shadow: 0 0 50px #ccc;
    -webkit-box-shadow: 0 0 50px #ccc;
}

/* TODO: fix padding  */
div#rss_ovr .feed {
  margin-left: 3px;
  padding-left: 19px;
  background: url("static/rss.png") no-repeat 0 50%;
  text-decoration: none;
  color: black;
}


div.tabpane div button {
    width: 6em;
    padding: 1px;
}

div#check_ovr {
    background-color:#fff;
    display:none;
    width: 70%;
    height: 80%;
    top: 10%;
    padding:15px;
    text-align:left;
    border:2px solid #333;
    opacity:0.8;
    -moz-border-radius:6px;
    -webkit-border-radius:6px;
    -moz-box-shadow: 0 0 50px #ccc;
    -webkit-box-shadow: 0 0 50px #ccc;
}

div#diff_table {
    display: inline;
    border: 0;
    padding: 0;
    margin: 0;
}

table td {
    border: 1px solid #c0c0c0;
    padding: 2px;
}
table.phdiff_table tr.title td {
    text-align:center;
    background-color: #f0f0f0;
    font-size: 120%;
    font-weight: bold;
}
table.phdiff_table tr.add {
    background-color: #f0fff0;
}
table.phdiff_table tr.del {
    background-color: #fff0f0;
}

p#spinner { text-align: center; }

div#version_list{
    display: inline;
    margin: 0;
    padding: 0;
    border: 0;
}

div#version_list table {
    margin: 2em;
}

div#diff_table {
    height: 90%;
    width: 95%;
    background-color:#ffffff;
    overflow: auto;
    position: absolute;
}

</style>

<script>
$(function() {

    on_tab_load();

    $('button#save').click(function() {
    });

    var triggers = $("button#save").overlay({
        mask: {
            color: '#ebecff',
            loadSpeed: 200,
            opacity: 0.9
        },
        closeOnClick: false,
        onLoad: function() {
            remove_main_keybindings();
            $("div#savediag form input").focus();
        },
        onClose: function() {
            setup_main_keybindings();
        },
    });

    $('button#check').click(function() {
        $.post("check", function(json) {
            }); //FIXME
    });

    $('button#deploy').click(function() {
        $.post("deploy",
            function(data){            });
    }); //FIXME

    // Version list pane
    $('div#version_list table').load('version_list', function() {

        $('img.rollback').click(function() {  // Setup rollback trigger
            cid = this.id;
            $.post("rollback", {commit_id: cid},
                function(data){
                    $('div#version_list table').load('version_list');
                });
        });

        $('img.view_ver_diff').click(function() {
            $('div#version_list').load('version_diff', {commit_id: this.id});
        });

        /*
        $("img.view_ver_diff[rel]").overlay({  // Setup commit diff trigger
            mask: {
                loadSpeed: 200,
                opacity: 0.9,
                onLoad: function () {
                    d = $('div#view_ver_diff');
                    d.html('<p>Diff in progress...</p><p id="spinner"><img src="static/spinner_big.gif" /></p>');
                    d.load('version_diff', {commit_id: this.id});
                }
            }
        });
        */

    });

    // FIXME: Check button should open the overlay
    // TODO: create Deploy overlay?

    // Check feedback overlay

    $("img#check[rel]").overlay({
        mask: {
            loadSpeed: 200,
            opacity: 0.9,
            onLoad: function () {
            dt = $('div#diff_table');
            dt.html('<p>Check in progress...</p><p id="spinner"><img src="static/spinner_big.gif" /></p>')
                // When loaded, run the check command using POST and display the output
                dt.load("check", {});
            }
        },
        closeOnClick: false,
        onLoad: function() {
            remove_main_keybindings();
            $("div#savediag form input").focus();
        },
        onClose: function() {
            setup_main_keybindings();
        },
    });

    // RSS overlay
    $("img#rss[rel]").overlay({ mask: {loadSpeed: 200, opacity: 0.9, }, });
});
</script>

