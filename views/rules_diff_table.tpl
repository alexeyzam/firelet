<img src="static/back.png"/> Back
% for hn, (added, removed) in diff_dict.iteritems():
<h4 class='dtt'>{{hn}}</h4>
<table class='phdiff_table'>
    % for r in added:
    <tr class="add"><td>{{r}}</td></tr>
    % end
    % for r in removed:
    <tr class="del"><td>{{r}}</td></tr>
    % end
</table>
% end

