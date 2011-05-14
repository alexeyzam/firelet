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
        <img src="/static/edit.png" title="Edit network" id="{{rid}}" rel="#editing_form" class="edit">
        <img src="/static/delete.png" title="Delete network" id="{{rid}}" class="delete">
    </td>
    <td>{{network.name}}</td>
    <td>{{network.ip_addr}}</td>
    <td>{{network.masklen}}</td>
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

<p><img src="static/new.png" rel="#editing_form" class="new"> New network</p>

<!-- Item editing or creation form -->
<div id="editing_form">
    <form id="editing_form">
       <fieldset>
          <h3>Network editing</h3>
          <p> Enter values and press the submit button. </p>
          <p>
             <label>Name *</label>
             <input type="text" name="name" pattern="[a-zA-Z0-9_]{2,512}" maxlength="30" />
          </p>
          <p>
             <label>Address *</label>
             <input type="text" name="ip_addr" pattern="[0-9.:]{7,}" maxlength="30" />
          </p>
          <p>
             <label>Netmask length *</label>
             <input type="text" name="masklen" pattern="[0-9]{1,2}" maxlength="2" />
          </p>
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

    $("table#items tr td img").fadeTo(0, 0.6);

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
            $.post("networks",{'action':'fetch','rid':rid}, function(json){
                $("form#editing_form input[type=text]").each(function(n,f) {
                    f.value = json[f.name];
                });
                $("form#editing_form input[name=token]").get(0).value = json['token'];
                set_form_trig();
            }, "json");
        },
        closeOnClick: false
    });


    // Send editing_form field values on submit

    // FIXME: validator is not showing error messages

   $("form#editing_form").validator().submit(function(e) {
        var form = $(this);
        // client-side validation OK
        if (!e.isDefaultPrevented()) {
            ff = $('form#editing_form').serializeArray();
            $.post("networks", ff, function(json){
                if (json.ok === true) {
                    $("img[rel]").each(function() {
                        $(this).overlay().close();
                    });
                    $('div.tabpane div').load('/networks');
                } else {
                    form.data("validator").invalidate(json);
                }
            }, "json");
            e.preventDefault();     // prevent default form submission logic
        } else {
            console.log('not ok');
        };
    });



    // Help overlay
    $("img#help[rel]").overlay({ mask: {loadSpeed: 200, opacity: 0.9, }, });
});
</script>
