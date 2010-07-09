<button id="save" rel="#prompt"><img src="static/save.png"  title="Save"> Save</button>
<br/>
<img id="check" src="static/check.png" rel="#check_ovr" title="Check">

<button id="check" rel="#prompt"><img src="static/check.png" rel="#check" title="Check"> Check</button>
<br/>
<button id="deploy" rel="#prompt"><img src="static/deploy.png"  title="Deploy"> Deploy</button>

<!-- check_feedback dialog -->
<div class="ovl" id="check_ovr">
    <h2>Configuration check</h2>
    <div id="diff_table">
    </div>
    <br />
</div>


<style>

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




});
</script>
