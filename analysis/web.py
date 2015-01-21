import urllib2
import urlparse

class Web(object):

    def __init__(self):
        self.urls_2xx = 0
        self.urls_3xx = 0
        self.urls_4xx = 0
        self.urls_5xx = 0

    def get_url(self,url):
        parsed_url = urlparse.urlparse(url)
        content = ""
        code = 0
        if parsed_url.scheme:
            try:
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
                #headers = { 'User-Agent' : 'Mozilla/5.0' }
                #req = urllib2.Request(url, None, headers)
                #response  = urllib2.urlopen(req)
                response = opener.open(url)
                #print response
                content = response.read()
                code = response.code
            except urllib2.HTTPError, error:
                content = error.read()
                code = error.code

        if 200 <= code < 300:
            self.urls_2xx += 1
        elif 300 <= code < 400:
            self.urls_3xx += 1
        elif 400 <= code < 500:
            self.urls_4xx += 1
        elif 500 <= code < 600:
            self.urls_5xx += 1

        return code, content

#W = Web()

#code, content = W.get_url("https://domain.opendns.com/imdb.com")

#with open("see.html", "w") as html_file:
#    html_file.write(content)