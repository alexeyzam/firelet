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
            %if rule.enabled == "1":
            <img class="action" src="/static/disable.png" title="Disable rule" action="disable">
            %elif rule.enabled == "0":
            <img class="action" src="/static/enable.png" title="Enable rule" action="enable">
            %end
            <img class="action" src="/static/delete.png" title="Delete rule" action="delete">
        </td>
        <td>
                % if rule.enabled =='1':
                <img src="/static/mark.png">
                % end
        </td>
        <td>{{rule.name}}</td>
        <td>{{rule.src}}</td>
        <td>{{rule.src_serv}}</td>
        <td>{{rule.dst}}</td>
        <td>{{rule.dst_serv}}</td>
        <td>{{rule.action}}</td>
        <td>{{rule.log_level}}</td>
        <td>{{rule.desc}}</td>
    </tr>
    % end
</table>



<script>
$(function() {

    on_tab_load();

    $('img.action').click(function() {
        tr = $(this).parents('tr');
        rid = tr.attr('id');
        token = tr.children().eq(10).innerText;
        action = $(this).attr('action');
        $('.tooltip').hide();
        $.post("ruleset", { action: action, token: token, rid: rid},
            function(data){
                $('div.tabpane div').load('/ruleset', function() {
                    if (action == "newabove") {
                        tr.load('ruleset_form', {rid: rid});
                    }
                });
            });
    });


    function insert_net_names() {
        $.post("net_names",{}, function(json){
            s = $("select#multisel");
            s.html("<option></option>");
            for (i in json.net_names)
                s.append("<option>"+json.net_names[i]+"</option>")
        })
    }


    /// Editing form ///

    $("table#items tr td").dblclick(function() {
        rid = $(this).parent().attr('id');
        $(this).parent().load('ruleset_form', {rid: rid}, function() {
        });
    })

    function set_form_trig() {
        // Remove routed networks on click
        $("div#selected p").click(function() {
            $(this).remove();
        })
    }

    function reset_form() {
        $("form#editing_form input")
        .val('')
        .removeAttr('checked');
        $("form#editing_form input[name=action]").val('save');
        $("div#selected").text('');
    }

    // Open the overlay form to create a new element
    $("img.new[rel]").overlay({
            mask: { loadSpeed: 200, opacity: 0.9 },
            onBeforeLoad: function() {
                reset_form();
                insert_net_names();
            },
            closeOnClick: false
    });


    // Add routed network when the user select it from the combo box
    $("select#multisel").change(function() {
        v = $("select#multisel").val();
        $("select#multisel").val('');
        if (v) $("div#selected").append("<p>"+v+"</p>")
        set_form_trig()
    })



    // Send editing_form field values on submit

    $("form#editing_form").validator().submit(function(e) {
        var form = $(this);
        // client-side validation OK
        if (!e.isDefaultPrevented()) {
        ff = $('form#editing_form').serializeArray();
        // extract the text in the paragraphs in div#selected and squeeze it
        routed = []
        $('div#selected p').each(function(i) {
            routed.push($(this).text())
        })
        // Append routes to the fields list
        ff.push({name: "routed", value: routed});
        $.post("hosts", ff, function(json){
            if (json.ok === true) {
                $("img[rel]").each(function() {
                    $(this).overlay().close();
                });
                $('div.tabpane div').load('/hosts');
            } else {
                form.data("validator").invalidate(json);
            }
        }, "json");
            e.preventDefault();     // prevent default form submission logic
        }
    });


});
</script>
