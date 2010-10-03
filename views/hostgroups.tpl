
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
    <tr><th></th><th>Name</th><th>Siblings</th></tr>
% for rid, hg in hostgroups:
    <tr id="{{rid}}">
    <td class="hea">
        <img src="/static/edit.png" title="Edit host group" id="{{rid}}" rel="#editing_form" class="edit">
        <img src="/static/delete.png" title="Delete host group" id="{{rid}}" class="delete">
    </td>
    <td>{{hg.name}}</td>
    <td>{{' '.join(hg.childs)}}</td>
    </tr>
% end
</table>

<p><img src="static/new.png" rel="#editing_form" class="new"> New hostgroup</p>

<!-- Item editing or creation form -->
<div id="editing_form">
    <form id="editing_form">
       <fieldset>
          <h3>Hostgroup editing</h3>
          <p> Enter values and press the submit button. </p>
          <p>
             <label>name *</label>
             <input type="text" name="name" pattern="[a-zA-Z0-9_]{2,512}" maxlength="30" />
          </p>
          <div id="multisel">
            <p>Siblings</p>
            <div id="selected">
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

    $("table#items tr td img").fadeTo(0, 0.6);

    $("table#items tr td img").hover(function() {
      $(this).fadeTo("fast", 1);
    }, function() {
      $(this).fadeTo("fast", 0.6);
    });

    $(function() {
        $('img.delete').click(function() {
            td = this.parentElement.parentElement;
            $.post("hostgroups", { action: 'delete', rid: td.id},
                function(data){
                    $('div.tabpane div').load('/hostgroups');
                });
        });
    });
    // Help overlay
    $("img#help[rel]").overlay({ mask: {loadSpeed: 200, opacity: 0.9, }, });


    // Form management //

    // Populate the siblings combo box based on the existing siblings
    function insert_sib_names() {
        $.post("sib_names",{}, function(json){
            s = $("select#multisel");
            s.html("<option></option>");
            for (i in json.sib_names)
                s.append("<option>"+json.sib_names[i]+"</option>")
        })
    }

    function set_form_trig() {
        // Remove siblings  on click
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
                insert_sib_names();
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
            $.post("hostgroups",{'action':'fetch','rid':rid}, function(json){
                $("form#editing_form input[type=text]").each(function(n,f) {
                    f.value = json[f.name];
                });
                $("form#editing_form input[name=token]").get(0).value = json['token'];
                ds = $("div#selected").text('');
                for (i in json.childs)
                    ds.append('<p>'+json.childs[i]+'</p>');
                set_form_trig();
            }, "json");
            insert_sib_names();
        },
        closeOnClick: false
    });


    // Add siblings when the user select it from the combo box
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
        mysiblings = []
        $('div#selected p').each(function(i) {
            mysiblings.push($(this).text())
        })
        // Append routes to the fields list
        ff.push({name: "siblings", value: mysiblings});
        $.post("hostgroups", ff, function(json){
            if (json.ok === true) {
                $("img[rel]").each(function() {
                    $(this).overlay().close();
                });
                $('div.tabpane div').load('/hostgroups');
            } else {
                form.data("validator").invalidate(json);
            }
        }, "json");
            e.preventDefault();     // prevent default form submission logic
        }
    });


});
</script>

