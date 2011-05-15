// Main jQuery script

// globals variables and functions

var selected_row = -1;

// Refresh message pane
function refresh_msg()
{
    setTimeout("refresh_msg()",2000);
    t = $("div#msgslot").scrollTop();
    th = $("table#msgs").height();
    delta = th - t - 100;
    if (delta < 10) { $("table#msgs").load("/messages"); }
    $.getJSON("save_needed", function(json){
        if (json.sn === true) $("div#savereset").show();
        else $("div#savereset").hide();
    });
}

//Disable shortcut key bindings
function remove_main_keybindings() {
    $('body').unbind('keypress');
}

// Refresh selected table row
// direction can be +1 or -1
function refresh_selected_row(direction) {
    if (selected_row > 0 && direction == -1) {
        selected_row--;
    } else{
        trs = $('table#items tbody tr')
        if  (selected_row < trs.length - 1 && direction == 1) {
            selected_row += direction;
        }
    }

    $('table#items tbody tr').css({
        backgroundColor: ''
    });
    $('table#items tbody tr').eq(selected_row).css({
        backgroundColor: '#f9f9f9',
    });
}

// Setup shortcut key bindings
function setup_main_keybindings() {
    var tabs = $("ul.css-tabs").data("tabs");
    var tabs_key_map = {
        114: 0, // Ruleset
        103: 1, // host Groups
        104: 2, // Hosts
        110: 3, // Networks
        115: 4, // Services
        109: 5, // Manage
        97: 6, // mAp
    }
    $('body').keypress(function(e) {
        var k = (e.keyCode ? e.keyCode : e.which);
        if (k in tabs_key_map) {
            tabs.click(tabs_key_map[k]);
            return;
        }
        switch (k) {
            case 67: // Shift Cancel
                break;

            case 83: // Shift Save
                $.getJSON("save_needed", function(json){
                    if (json.sn === true)
                        $("img#saveimg").overlay().load();
                });
                break;

            case 65: // Shift Add
                break;

            case 106: // J: move down
                refresh_selected_row(1);
                break;

            case 107: // K: move up
                refresh_selected_row(-1);
                break;

            case 13: // Enter
                if (selected_row != -1) {
                    tr = $('table#items tbody tr').eq(selected_row);
                    console.log(tr);
                    //FIXME
                    $("div#editing_form").overlay().load();
                }
                break;

            case 78: // Shift New
                $("img.new[rel]").overlay().load();
                //FIXME
                break

            default:
                //console.log(k);
        }
    });
}

// Ran on tab change or reload
function on_tab_load() {
    // Setup new help overlay
    $("img#help[rel]").overlay({mask: {loadSpeed: 200, opacity: 0.9, }, });

    // Reset selected row
    selected_row = -1;

    // Setup tooltips and hovering
    $("table#items tr td img[title]").tooltip({
        tip: '.tooltip',
        effect: 'fade',
        fadeOutSpeed: 100,
        predelay: 800,
        position: "bottom right",
        offset: [15, 15]
    });

    $("table#items tr td img").fadeTo(0, 0.6);

    $("table#items tr td img").hover(function() {
      $(this).fadeTo("fast", 1);
    }, function() {
      $(this).fadeTo("fast", 0.6);
    });
}


// Execute on main page load
$(function() {

    // Setup tabs
    $("ul.css-tabs").tabs("div.tabpane > div", {
        effect: 'ajax',
        history: true,
        onClick: function() {
            on_tab_load();
        }
    });
    //FIXME: history not updated by shortcuts

    //FIXME: tooltips do not disappear sometimes

    // Start refreshing message pane
    refresh_msg();

    setTimeout(function() {
        $("div#msgslot").scrollTop(1000);
    },500);

    //TODO: put focus on save input field
    // Setup triggers for the save and reset buttons

    $("div#savereset").hide();

    $.getJSON("save_needed", function(json){
        if (json.sn === true) $("div#savereset").show();
    });

    $("div#savereset img[title]").tooltip({
        tip: '.tooltip',
        effect: 'fade',
        fadeOutSpeed: 100,
        predelay: 800,
        position: "bottom right",
        offset: [15, -30]
    });

    $("div#savereset img").fadeTo(0, 0.6);

    $("div#savereset img").hover(function() {
      $(this).fadeTo("fast", 1);
    }, function() {
      $(this).fadeTo("fast", 0.6);
    });


    $('img#reset').click(function() {
      $.post("reset");
      $('div#savereset').hide();
    });

    // Setup triggers for the save form

    var triggers = $("img#saveimg").overlay({
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

    $("#savediag form").submit(function(e) {
        var input = $("input", this).val();
        $.post("save",{msg: input}, function(json) {
            triggers.eq(0).overlay().close();
            $('div#savereset').hide();
        },"json");
        return e.preventDefault();
    });

    setup_main_keybindings();

});
