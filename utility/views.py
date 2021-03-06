from django.http import HttpResponseForbidden
from cloud_ide.fiddle.jsonresponse import JsonResponse
import urllib2, base64, urlparse
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup as BS

def scrape(request):    
    url = request.GET['url']
    if not urlparse.urlparse(url).scheme[0:4] == 'http':
        return HttpResponseForbidden()
    response_dict = {}
    success = False
    try:
        response = urllib2.urlopen(url)
        html = response.read(200000) #200 kiloBytes

        document = BS(html)

        body = str(document.body)
        resources = []
        inlineJavascriptBlocks = []
        inlineCssBlocks = []

        for styleSheet in document.findAll('link', attrs={'rel': 'stylesheet'}):
            resources.append(styleSheet.get('href'))

        for style in document.findAll('style'):
            inlineCssBlocks.append(style.string)

        scripts = document.findAll('script')
        for script in scripts:
            externalJavascriptSource = script.get('src', None)
            if externalJavascriptSource:
                resources.append(externalJavascriptSource)
            else:
                # if script is not a template
                scriptType = script.get('type', None)
                if not scriptType or scriptType is 'text/javascript':
                    inlineJavascriptBlocks.append(script.string)
    except urllib2.HTTPError:
        response_dict.update({'error': 'HTTP Error 404: Not Found'})
    except HTMLParseError:
        response_dict.update({'error': 'malformed HTML'})
    except urllib2.URLError:
        response_dict.update({'error': 'service not available'})
    else:
        success = True
        response_dict.update({
            'resources': resources,
            'inlineJavascriptBlocks': inlineJavascriptBlocks,
            'inlineCssBlocks': inlineCssBlocks,
            'body': base64.b64encode(body)
        })
    response_dict.update({'success': success})
    return JsonResponse(response_dict)