
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
        <tr><th></th><th>Name</th><th>Iface</th><th>IP Address</th><th>Netmask l.</th><th>Local Fw</th>
            <th>Network Fw</th><th>Management</th><th>Routed networks</th></tr>
    </thead>
% for rid, h in hosts:
    <tr id="{{rid}}">
    <td class="hea">
        <img src="/static/edit.png" title="Edit host" id="{{rid}}" rel="#editing_form" class="edit">
        <img src="/static/delete.png" title="Delete host" id="{{rid}}" class="delete">
    </td>
    <td>{{h.hostname}}</td>
    <td>{{h.iface}}</td>
    <td>{{h.ip_addr}}</td>
    <td>{{h.masklen}}</td>
    <td>
            % if h.local_fw=='1':
            <img src="/static/mark.png">
            % end
    </td>
    <td>
            % if h.network_fw =='1':
            <img src="/static/mark.png">
            % end
    </td>
    <td>
            % if h.mng =='1':
            <img src="/static/mark.png">
            % end
    </td>
    <td>{{' '.join(h.routed)}}</td>
    </tr>
% end
</table>

<p><img src="static/new.png" rel="#editing_form" class="new"> New host</p>

<!-- Item editing or creation form -->
<div id="editing_form">
    <form id="editing_form">
       <fieldset>
          <h3>Host editing</h3>
          <p> Enter bad values and then press the submit button. </p>

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
            <input type="checkbox" name="local_fw" />
          </p>
          <p>
            <label>Network firewall</label>
            <input type="checkbox" name="network_fw" />
          </p>
          <p>
            <label>Management interface</label>
            <input type="checkbox" name="mng" />
          </p>
          <div id="multisel">
            <p>Routed networks</p>
            <div id="selected">
                <p>ex1</p>
                <p>ex2</p>
                <p>ex3</p>
            </div>
            <select id="multisel">
                <option></option>
                <option value="11">11</option>
                <option value="22">22</option>
                <option value="33">33</option>
                <option value="44">44</option>
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


    $('img.delete').click(function() {
        $.post("hosts", { action: 'delete', rid: this.id},
            function(data){
                $('div.tabpane div').load('/hosts');
            });
    });

    // Open the overlay form to create a new element
    $("img.new[rel]").overlay({
            mask: { loadSpeed: 200, opacity: 0.9 },
            onBeforeLoad: function() {
                $("form#editing_form input").each(function(n,f) {
                    f.value = '';
                    f.checked = false;
                });
            },
            closeOnClick: false
    });

    // If the form is being used to edit an existing item,
    // load the actual values
    $("img.edit[rel]").overlay({
        mask: { loadSpeed: 200, opacity: 0.9 },
        onBeforeLoad: function(event, tabIndex) {
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
            }, "json");
        },
        closeOnClick: false
    });

    // Remove routed networks on click
    $("div#selected p").click(function() {
        $(this).remove();
    })

    // Add routed network when selected from the combo box
    $("select#multisel").change(function() {
        v = $("select#multisel").val();
        $("select#multisel").val('');
        if (v) $("div#selected").append("<p>"+v+"</p>")
        $("div#selected p").click(function() {
            $(this).remove();
        })
    })



    // Send editing_form field values on submit

    $("form#editing_form").validator().submit(function(e) {
        var form = $(this);
        // client-side validation OK
        if (!e.isDefaultPrevented()) {
        ff = $('form#editing_form').serializeArray();
        // extract the text in the paragraphs in div#selected and squeeze it
        v = $('div#selected').text().replace(/\s+/g, ' ').trim();
        // Append to the fields list
        ff.push({name: "routed", value: v});
        console.log(ff);
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


    // Help overlay
    $("img#help[rel]").overlay({ mask: {loadSpeed: 200, opacity: 0.9, }, });
});
</script>

