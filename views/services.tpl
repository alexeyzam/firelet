
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
        <tr><th></th><th>Name</th><th>Protocol</th><th>Ports / ICMP Type</th></tr>
    </thead>
% for rid, service in services:
    <tr id="{{rid}}">
    <td class="hea">
        <img src="/static/edit.png" title="Edit service" id="{{rid}}" rel="#editing_form" class="edit">
        <img src="/static/delete.png" title="Delete service" id="{{rid}}" class="delete">
    </td>
    <td>{{service.name}}</td>
    <td>{{service.protocol}}</td>
    <td>{{service.ports}}</td>
    </tr>
% end
</table>

<p><img src="static/new.png" rel="#editing_form" class="new"> New service</p>

<!-- Item editing or creation form -->
<div id="editing_form">
    <form id="editing_form">
       <fieldset>
          <h3>Service editing</h3>
          <p> Enter values and press the submit button. </p>
          <p>
             <label>Name *</label>
             <input type="text" name="name" pattern="[a-zA-Z0-9_]{2,512}" maxlength="30" />
          </p>
          <p>
            <label>Protocol</label>
            <select name="protocol" id="protocol">
                <option>TCP</option>
                <option>UDP</option>
                <option>ICMP</option>
                <option>IP</option>
                <option>ESP</option>
                <option>AH</option>
          </select>
          </p>
          <p id="ports">
             <label>Ports *</label>
             <input type="text" name="ports" pattern="[0-9,:-]{0,128}" maxlength="30" />
          </p>
          <p id="icmp_type">
              <label>ICMP Type</label>
              <select name="icmp_type" id="icmp_type">
                <option value="">all</option>
                <option value="0">echo-reply</option>
                <option value="3">destination-unreachable</option>
                <option value="4">source-quench</option>
                <option value="5">redirect</option>
                <option value="8">echo-request</option>
                <option value="9">router-advertisement</option>
                <option value="10">router-solicitation</option>
                <option value="11">ttl-exceeded</option>
                <option value="12">parameter-problem</option>
                <option value="13">timestamp-request</option>
                <option value="14">timestamp-reply</option>
                <option value="17">address-mask-request</option>
                <option value="18">address-mask-reply</option>
              </select>
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
            $.post("services", { action: 'delete', rid: td.id},
                function(data){
                    $('div.tabpane div').load('/services');
                });
        });
    });

    // Editing form //

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
            $.post("services",{'action':'fetch','rid':rid}, function(json){
                $("form#editing_form input[type=text]").each(function(n,f) {
                    f.value = json[f.name];
                });
                $("form#editing_form select[name=protocol]").get(0).value = json['protocol'];
                if (json.protocol === 'ICMP')
                    $("form#editing_form select[name=icmp_type]").get(0).value = json.ports;
                $("form#editing_form input[name=token]").get(0).value = json['token'];
                 $("form#editing_form select[name=protocol]").change();
                set_form_trig();
            }, "json");
        },
        closeOnClick: false
    });

    // Switch between showing  ICMP Type/port selector/nothing depending on the selected protocol

    $("form#editing_form select[name=protocol]").change(function() {
        switch (this.value) {
            case 'ICMP':
                $("form#editing_form p#icmp_type").show();
                $("form#editing_form p#ports").hide();
                break;
            case 'TCP':
            case 'UDP':
                $("form#editing_form p#icmp_type").hide();
                $("form#editing_form p#ports").show();
                break;
            default:
                $("form#editing_form p#icmp_type").hide();
                $("form#editing_form p#ports").hide();
        }
    });

    // Send editing_form field values on submit

   $("form#editing_form").validator().submit(function(e) {
        var form = $(this);
        // client-side validation OK
        if (!e.isDefaultPrevented()) {
            ff = $('form#editing_form').serializeArray();
            $.post("services", ff, function(json){
                if (json.ok === true) {
                    $("img[rel]").each(function() {
                        $(this).overlay().close();
                    });
                    $('div.tabpane div').load('/services');
                } else {
                    form.data("validator").invalidate(json);
                }
            }, "json");
            e.preventDefault();     // prevent default form submission logic
        } else {
            console.log('not ok');
        };
    });


});
</script>

