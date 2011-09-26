
<td class="hea">
    <img id="formsave" src="/static/save.png" title="Save" action="save">
    <img id="formback" src="/static/back.png" title="Cancel" action="cancel">
    <img id="formdel" src="/static/delete.png" title="Delete rule" action="delete">
</td>
<td>
    <input type="checkbox" name="enabled"
        % if rule.enabled =='1':
        checked=""
        % end
    />
</td>
<td><input type="text" name="name" value="{{rule.name}}" /></td>
<td>
    <select name="src">
        % for i in objs:
            % s = ' selected="" ' if rule.src == i else ''
        <option {{s}}>{{i}}</option>
        % end
    </select>
</td>
<td>
    <select name="src_serv">
        % for i in services:
            % s = ' selected="" ' if rule.src_serv == i else ''
        <option {{s}}>{{i}}</option>
        % end
    </select>
</td>
<td>
    <select name="dst">
        % for i in objs:
            % s = ' selected="" ' if rule.dst == i else ''
        <option {{s}}>{{i}}</option>
        % end
    </select>
</td>
<td>
    <select name="dst_serv">
        % for i in services:
            % s = ' selected="" ' if rule.dst_serv == i else ''
        <option {{s}}>{{i}}</option>
        % end
    </select>
</td>
<td>
    <select name="rule_action">
        % for i in ('ACCEPT', 'DROP'):
        %   s = ' selected="" ' if rule.action == i else ''
        <option {{s}}>{{i}}</option>
        % end
    </select>
</td>
<td>
    <select name="log">
        % for i in (0,1,2,3):
        %   s = ' selected="" ' if rule.log_level == str(i) else ''
        <option{{s}}>{{i}}</option>
        % end
    </select>
</td>
<td><input type="text" name="desc" value="{{rule.desc}}" /></td>
<input type="hidden" value="{{rule._token()}}" />
<input type="hidden" name="action" value="save" />
<input type="hidden" name="rid" value="{{rid}}" />



<script>
$(function() {
    // FIXME: disable shortcuts while typing in the form

    // Perform cancel or deleto or send the form contents upon save
    $('img#formsave').click(function() {
        tr = $(this).parents('tr');
        ff = tr.find('input,select').serializeArray();
        rid = $(this).parent().attr('id');
        ff.rid = rid;
        $('.tooltip').hide();
        $.post("ruleset", ff,
            function(data){
                $('div.tabpane div').load('/ruleset');
            });
    });

    // Perform an action on table row and refresh the table
    function run_action(tr, action, data) {
        rid = tr.attr('id');
        token = tr.children().eq(10).innerText;
        $('.tooltip').hide();
        $.post("ruleset", { action: action, token: token, rid: rid}, function(data){
            $('div.tabpane div').load('/ruleset', function() {
                if (action == "newabove") {
                    tr.load('ruleset_form', {rid: rid});
                }
            });
        });
    }

    $('img#formback').click(function() {
        $('div.tabpane div').load('/ruleset');
    });

    $('img#formdel').click(function() {
        tr = $(this).parents('tr');
        run_action(tr, 'delete')
    });
});
</script>
