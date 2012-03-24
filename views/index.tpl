<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type">
%if not logged_in:
<div>
    <h2>Login</h2>
    <p>Please insert your credentials:</p>
    <form action="login" method="post">
        <input type="text" name="user" />
        <input type="password" name="pwd" />
        <br/><br/>
        <button type="submit" > OK </button>
        <button type="button" class="close"> Cancel </button>
    </form>
    <br />
</div>
<style>
div {
    color: #777;
    margin: auto;
    width: 20em;
    text-align: center;
}
input {
    background: #f8f8f8;
    border: 1px solid #777;
    margin: auto;
}
input:hover { background: #fefefe}
</style>
%end
%if logged_in:
<title>Firelet</title>

<script src="static/jquery.tools.min.js"></script>

<link rel="stylesheet" type="text/css" href="static/main.css" />

</head>
<body>

    <div id="header"><div>Firelet</div></div>
    <div id="pageLogin">
    <span><a id="logout" href="/logout">Logout</a></span>
    </div>
    <div id="savereset">
        <span>
            <img src="static/save.png"  rel="#savediag" title="Save" id="saveimg">
        </span>
        <span>
            <img src="static/reset.png" title="Reset" id="reset">
        </span>
    </div>

    <ul class="css-tabs">
        <li><a href="ruleset">Ruleset</a></li>
        <li><a href="hostgroups">Host Groups</a></li>
        <li><a href="hosts">Hosts</a></li>
        <li><a href="networks">Networks</a></li>
        <li><a href="services">Services</a></li>
        <li><a href="manage">Manage</a></li>
        <li><a href="map">Map</a></li>
    </ul>

    <div class="tabpane"><div style="display:block"></div></div>

    <div id="msgpane">
        <div id="gradient"></div>
        <div id="msgslot">
            <table id="msgs">
            </table>
        </div>
    </div>

    <div id="footer">
        <p>Distributed firewall management</p>
    </div>



<!-- save dialog -->
<div class="modal" id="savediag">
    <h2>Save configuration</h2>
    <p>Please insert a change description</p>
    <form>
        <input />
        <button type="submit"> OK </button>
        <button type="button" class="close"> Cancel </button>
    </form>
    <br />
</div>

<!-- login dialog -->
<div class="modal" id="loginform">
    <h2>Login</h2>
    <p>Please insert your credentials:</p>
    <form>
        <input type="text" name="user" value="username here, pwd below" />
        <input type="password" name="pwd" value="" />
        <br/><br/>
        <button type="submit"> OK </button>
        <button type="button" class="close"> Cancel </button>
    </form>
    <br />
</div>

<script type="text/javascript" src="static/js/main.js"></script>

</body>

</html>
% end
