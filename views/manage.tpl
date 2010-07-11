<img id="help" src="static/help.png" rel="div#help_ovr" title="Help">
<div id="help_ovr">
    <h4>Contextual help: Manage</h4>
    <p>TODO</p>
    <p>Here some nice Lorem ipsum:</p>
    <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
    <br/>
    <p>Press ESC to close this window</p>
</div>


<button id="save" rel="#prompt"><img src="static/save.png"  title="Save"> Save</button>
<br/>
<img id="check" src="static/check.png" rel="#check_ovr" title="Check">

<button id="check" rel="#prompt"><img src="static/check.png" rel="#check" title="Check"> Check</button>
<br/>
<button id="deploy" rel="#prompt"><img src="static/deploy.png"  title="Deploy"> Deploy</button>

<div id="version_list">
    <table>
    </table>
</div>

<!-- check_feedback dialog -->
<div class="ovl" id="check_ovr">
    <h2>Configuration check</h2>
    <div id="diff_table">
    </div>
    <br />
</div>


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
    opacity:0.8;
    -moz-border-radius:6px;
    -webkit-border-radius:6px;
    -moz-box-shadow: 0 0 50px #ccc;
    -webkit-box-shadow: 0 0 50px #ccc;
}


div.tabpane div button {
    width: 6em;
    padding: 1px;
}

div#check_ovr {
    background-color:#fff;
    display:none;
    width: 70em;
    padding:15px;
    text-align:left;
    border:2px solid #333;

    opacity:0.8;
    -moz-border-radius:6px;
    -webkit-border-radius:6px;
    -moz-box-shadow: 0 0 50px #ccc;
    -webkit-box-shadow: 0 0 50px #ccc;
}
div#check_ovr div#diff_table {
    display: inline;
    border: 0;
    padding: 0;
    margin: 0;
}

table td {
    border: 1px solid #c0c0c0;
    padding: 2px;
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
</style>

<script>
$(function() {

    $('button#save').click(function() {
        $.post("save",
            function(data){            });
    });

    $('button#check').click(function() {
        $.post("check", function(json) {
            console.log(json.diff_table);
            });
    });

    $('button#deploy').click(function() {
        $.post("deploy",
            function(data){            });
    });

    $('div#version_list table').load('version_list', function() {
        $('img.rollback').click(function() {
            cid = this.id;
            $.post("rollback", {commit_id: cid},
                function(data){
                    $('div#version_list table').load('version_list');
                });
        });
    });



    // Check feedback overlay

    var over = $("img[rel]").overlay({
        mask: {
            loadSpeed: 200,
            opacity: 0.9,
            onLoad: function () {
            dt = $('div#diff_table');
            dt.html('<p>Check in progress...</p><p id="spinner"><img src="static/spinner_big.gif" /></p>')
                // When loaded, run the check command using POST and display the output
                $.post("check", function(json) {
                        dt.html(json.diff_table);
                });
            }
        },
        closeOnClick: false
    });

    // Help overlay
    $("img.help[rel]").overlay();

});
</script>
