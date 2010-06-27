
<style>
table#msgs tr td.hea {
    width: 20px;
    vertical-align:middle;
}
table#msgs tr td.ts { width: 5em; }
</style>

<table id="msgs">
    <thead>
        <tr><th></th><th>Time</th><th>Message</th></tr>
    </thead>

% for type, ts, s in messages:
    <tr>
    <td class="hea">
        <img src="/static/{{type}}.png">
    </td>
    <td class="ts">{{ts}}</td>
    <td>{{s}}</td>
    </tr>
% end
</table>

