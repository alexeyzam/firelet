
<td class="hea">
    <img class="action" src="/static/save.png" title="Save" action="save">
    <img class="action" src="/static/back.png" title="Cancel" action="cancel">
    <img class="action" src="/static/delete.png" title="Delete rule" action="delete">
</td>
<td>
    <input type="checkbox" name="'+i+'"
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
    <select name="action">
        % for i in ('ACCEPT', 'DROP'):
        %   s = ' selected="" ' if rule.action == i else ''
        <option {{s}}>{{i}}</option>
        % end
    </select>
</td>
<td>
    <select name="log">
        % for i in (0,1,2):
        %   s = ' selected="" ' if rule.log_level == str(i) else ''
        <option{{s}}>{{i}}</option>
        % end
    </select>
</td>
<td><input type="text" name="desc" value="{{rule.desc}}" /></td>
<td><input type="hidden" token="'+i+'" value="{{rule._token()}}" /></td>


