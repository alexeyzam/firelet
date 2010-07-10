<tr><th>Author</th><th>Date</th><th>Message</th><th>Rollback</th></tr>
% for author, date, msgs, commit in version_list:
<tr>
    <td>{{author}}</td>
    <td>{{date}}</td>
    <td>{{'<br/>'.join(msgs)}}</td>
    <td><img src="static/rollback.png" class="rollback" id="{{commit}}"/></td>
</tr>
% end
