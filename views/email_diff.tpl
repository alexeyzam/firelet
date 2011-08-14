<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <style type="text/css">
div.bu {
    border:1px solid green; border-left:3px solid green; padding:2px; background:#f0fff0; width:auto;
}
        </style>
    </head>
    <body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0">
        
        %for item, added in d['items']:
            %if added=='add':
        <div style="border:1px solid green;border-left:3px solid
        green;margin:1px;padding:2px;background:#f0fff0; width:auto;">{{item}}</div>
            %else:
        <div style="border:1px solid green;border-left:3px solid
        red;margin:1px;padding:2px;background:#fff0f0; width:auto;">{{item}}</div>
            %end
        %end

        <p>This is an automated email message from Firelet</p>
    </body>
</html>
