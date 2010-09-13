
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

/* Form validation error message */

.error {
    z-index: 30055;
    height:15px;
    background-color: #eeeeff;
    border:1px solid #000;
    font-size:11px;
    color:#000;
    padding:3px 10px;
    margin-left:20px;


    /* CSS3 spicing for mozilla and webkit */
    -moz-border-radius:4px;
    -webkit-border-radius:4px;
    -moz-border-radius-bottomleft:0;
    -moz-border-radius-topleft:0;
    -webkit-border-bottom-left-radius:0;
    -webkit-border-top-left-radius:0;

    -moz-box-shadow:0 0 6px #ddd;
    -webkit-box-shadow:0 0 6px #ddd;
}
div#multisel {
    margin: 0;
    padding: 0.1em;
    display: block;
    border: 0;
    background-color: transparent;
}
div#multisel div#selected {
    margin: 0 0 0 4em;
    padding: 0 2px 0 2px;
    display: block;
    border: 1px #333 solid;
    width: 20em;
    background: #fafafa;
}
div#multisel div#selected p {
    margin: 0;
    padding: 0;
    height: 1em;
    cursor: default;
}
div#multisel div#selected p:hover {
    text-decoration: line-through;
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
            %if rule.enabled == "1":
            <img class="action" src="/static/disable.png" title="Disable rule" action="disable">
            %elif rule.enabled == "0":
            <img class="action" src="/static/enable.png" title="Enable rule" action="enable">
            %end
            <img class="action" src="/static/delete.png" title="Delete rule" action="delete">
            <img src="/static/edit.png" title="Edit rule" id="{{rid}}" rel="#editing_form" class="edit">
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
        <td>{{rule._token()}}</td>

    </tr>
    % end
</table>

<!-- Item editing or creation form -->
<div id="editing_form">
    <form id="editing_form">
       <fieldset>
          <h3>Rule editing</h3>
          <p> Enter values and press the submit button. </p>

          <p>
             <label>hostname *</label>
             <input type="text" name="hostname" pattern="[a-zA-Z0-9_]{2,512}" maxlength="30" />
          </p>
          <p>
             <label>interface *</label>
             <input type="text" name="iface" pattern="[a-zA-Z0-9]{2,32}" maxlength="30" />
          </p>
          <p>
             <label>IP address *</label>
             <input type="text" name="ip_addr" pattern="[0-9.:]{7,}" maxlength="30" />
          </p>
          <p>
             <label>Netmask length *</label>
             <input type="text" name="masklen" pattern="[0-9]{1,2}" maxlength="2" />
          </p>
          <p>
            <label>Local firewall</label>
            <input type="checkbox" name="local_fw" value="local_fw" />
          </p>
          <p>
            <label>Network firewall</label>
            <input type="checkbox" name="network_fw" value="network_fw" />
          </p>
          <p>
            <label>Management interface</label>
            <input type="checkbox" name="mng" value="mng" />
          </p>
          <div id="multisel">
            <p>Routed networks</p>
            <div id="selected">
                <p></p>
            </div>
            <select id="multisel">
                <option></option>
            </select>
          </div>
          </br>
          <button type="submit">Submit</button>
          <button type="reset">Reset</button>
          <input type="hidden" name="action" value="save" />
          <input type="hidden" name="rid" value="" />
          <input type="hidden" name="token" value="" />
       </fieldset>
    </form>
    <p>Enter and Esc keys are supported.</p>
</div>


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


    /// Editing form ///
    /*
    $("table#items tr td").dblclick(function() {

        $(this).parent().children().each(function(i) {
            content = $(this).html()
            switch (i) {
                case 1:
                $(this).html('<input type="checkbox" name="'+i+'" checked="" />');
                break;
                case 2:
                $(this).html('<input type="text" name="'+i+'" value="'+content+'" />');
                break;
                case  7:
                $(this).html('<select name="action"><option>Accept</option><option>Drop</option></select>');
                $(this).value = content
                break;
                case  8:
                $(this).html('<select name="log"><option>0</option><option>1</option><option>2</option></select>');
                $(this).value = content
                break;
                case  9:
                $(this).html('<input type="text" name="'+i+'" value="'+content+'" />');
                break;
                case  10:
                $(this).html('<input type="hidden" token="'+i+'" value="'+content+'" /><img src="">');
                break;

            }
        });
    })
    */

    $("table#items tr td").dblclick(function() {
        rid = $(this).parent().attr('id');
        $(this).parent().load('ruleset_form', {rid: rid}, function() {
            console.log();
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

    // If the form is being used to edit an existing item,
    // load the actual values
    $("img.edit[rel]").overlay({
        mask: { loadSpeed: 200, opacity: 0.9 },
        onBeforeLoad: function(event, tabIndex) {
            reset_form();
            rid = this.getTrigger()[0].id;
            $("form#editing_form input[name=rid]").get(0).value = rid;
            $.post("hosts",{'action':'fetch','rid':rid}, function(json){
                $("form#editing_form input[type=text]").each(function(n,f) {
                    f.value = json[f.name];
                });
                $("form#editing_form input[type=checkbox]").each(function(n,f) {
                    f.checked = Boolean(json[f.name]);
                });
                $("form#editing_form input[name=token]").get(0).value = json['token'];
                ds = $("div#selected").text('');
                for (i in json.routed)
                    ds.append('<p>'+json.routed[i]+'</p>');
                set_form_trig();
            }, "json");
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

