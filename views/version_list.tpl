% if version_list:
<tr><th>Author</th><th>Date</th><th>Message</th><th>Actions</th></tr>
% end
% if not version_list:
<tr><th>(No saved configurations)</th></tr>
% end
% for author, date, msgs, commit in version_list:
<tr>
    <td>{{author}}</td>
    <td>{{date}}</td>
    <td>{{'<br/>'.join(msgs)}}</td>
    <td>
        <img src="static/rollback.png" class="rollback" id="{{commit}}"/>
        <img src="static/mag.png" class="view_ver_diff" id="{{commit}}"/>
    </td>
</tr>
% end
