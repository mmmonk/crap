from mod_python import apache
import socket

def handler(req):

    req.content_type = "text/html"

    out = """<!doctype html><html><head>
<style type="text/css">
body { font: normal normal 12px Verdana, Geneva, sans-serif;
color: #cccccc; background: #092a2c none repeat scroll top left;
padding: 0 40px 40px 40px; }
a:link { text-decoration:none; color: #00cbcc; }
a:visited { text-decoration:none; color: #00cbcc; }
a:hover { text-decoration:underline; color: #00696e; }
</style>
"""
    if req.status == 400:
        out += "<title>Bad Request - 400</title>"+\
            "</head><body><h1>Sorry <a href=\"https://en.wikipedia.org"+\
            "/wiki/List_of_HTTP_status_codes\">Bad Request - 400</a>"+\
            "</h1><br/>The request cannot be fulfilled due to bad syntax."

    elif req.status == 403:
        out += "<title>Forbiden - 403</title>"+\
            "</head><body><h1>Sorry <a href=\"https://en.wikipedia.org"+\
            "/wiki/HTTP_403\">Forbiden - 403</a>"+\
            "</h1><br/>It looks like you are not allowed to view this item."

    elif req.status == 404:
        out += "<title>Not Found - 404</title>"+\
            "</head><body><h1>Sorry <a href=\"https://en.wikipedia.org"+\
            "/wiki/HTTP_404\">Not Found - 404</a>"+\
            "</h1><br/>It looks like you are trying to reach none existing"+\
            " object."
    elif req.status == 200:
        """
        this is to prevent finding the name of this file
        """
        req.status = 404
        out += "<title>Not Found - 404</title>"+\
            "</head><body><h1>Sorry <a href=\"https://en.wikipedia.org"+\
            "/wiki/HTTP_404\">Not Found - 404</a>"+\
            "</h1><br/>It looks like you are trying to reach none existing"+\
            " object."
    else:
        out += "<title>%s</title>" % (req.status)+\
            "</head><body><h1>HTTP status code: %s</h1><br/>" % (req.status)

    out += "<br/><br/>Please be nice and go play somewhere else."+\
        "<br/>Use <a href=\"https://google.com\">this<a>, "+\
        "<a href=\"https://startpage.com\">this</a> or "+\
        "<a href=\"https://duckduckgo.com\">this</a> to find something."+\
        "<br/>If you are looking for something else try "+\
        "<a href=\"https://kickass.so/\">this</a> or any other torrent"+\
        " site.<br/><br/><br/></body></html>"

    NOTBLOCKED = ["127.0.0.1","::1","0.0.0.0","::"]
    peerip = req.connection.remote_addr[0]

    if peerip not in NOTBLOCKED:
        BOTS = ["ZmEu","Morfeus Fucking Scanner","-"]
        INUA = ["/bin/bash", "rm -rf", "User-Agent", "passwd"]

        browser = req.headers_in
        try:
            useragent = browser['User-Agent']
        except:
            useragent = "-"

        times = 1
        if useragent in BOTS:
            times = 3

        for nuas in INUA:
            if nuas in useragent:
                times = 3
                break

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_address = '/tmp/hostile_blocker'
        try:
            sock.connect(server_address)
            sock.sendall("%s %s" % (peerip,times))
        except:
            pass
        finally:
            sock.close()

    req.write(out)
    return apache.OK
