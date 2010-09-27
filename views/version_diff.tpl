<table class="phdiff_table">
<img src="static/back.png"/> Back
% for s, t  in li:
<tr class="{{t}}"><td>{{s}}</td></tr>
% end
</table>

<script>
    $('img').click(function(){
        $('div.tabpane div').load('/manage');
    });
</script>
