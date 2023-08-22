#!/usr/bin/env python3
"""
    Extract all color codes used in CSS in a website, reasonably sorted by HSV.

    No third party dependencies.

    Usage:
        ./csscolors.py https://www.example.com/fromhere


TODO:
    - support all possible CSS color values
        i.e. hex, hexa, rgb, rgba, hsl, hsla, named
    - print colored output and more info about colors
        i.e. assign names to known colors, rgb/hsv table, ...
"""

from html.parser import HTMLParser
import re
from sys import argv, stderr
from urllib.error import URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


class StyleExtractor(HTMLParser):
    """
        HTML parser to extract stylesheets from html code.

        - Download external stylesheets.
        - <style> tags
        - style= attributes
    """

    stylesheets = []
    styledata = False
    baseurl = ''

    def feed(self, text, _baseurl):
        self.baseurl = _baseurl
        super().feed(text)

    def handle_starttag(self, tag, attrs):
        css = ''

        if tag == 'style':
            self.styledata = True

        elif tag == 'link' and ('rel', 'stylesheet') in attrs:
            try:
                url = next(v for k,v in attrs if k == 'href')
            except StopIteration:
                pass
            else:
                css = http_get(urljoin(self.baseurl, url))

        else:
            css = next((v for k,v in attrs if k == 'style'), '')

        if css:
            self.stylesheets.append(css)

    def handle_endtag(self, tag):
        self.styledata = False

    def handle_data(self, data):
        if self.styledata:
            self.stylesheets.append(data)


def get_baseurl(url):
    """ Extract the base url from a random given url. """

    urlparts = urlparse(url)
    return urlunparse((urlparts.scheme, urlparts.netloc, '','','',''))


def http_get(url):
    """ Return content from webpage using urlopen. """

    request = Request(url, data=None, headers={
        # Circumvent blocking of scripts on some sites.
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0'
        })
    try:
        return urlopen(request).read().decode('utf-8')
    except URLError as err:
        print(err, file=stderr)
        return ''


def color_hex2hsv(hexval):
    """
        Convert a six-digit hexvalue to HSV.
    """

    hexval = hexval.lstrip('#')
    r = int(hexval[0:2], 16)/255.0
    g = int(hexval[2:4], 16)/255.0
    b = int(hexval[4:6], 16)/255.0

    cmin = min(r, g, b)
    cmax = max(r, g, b)
    delta = cmax - cmin

    h = 60
    if delta == 0.0:
        h = 0
    elif cmax == r:
        h *= ((g - b)/delta) % 6
    elif cmax == g:
        h *= ((b - r)/delta) + 2
    elif cmax == b:
        h *= ((r - g)/delta) + 4

    s = 0
    if cmax != 0.0:
        s = delta / cmax

    #v = cmax

    return h, s, cmax


def extract_colors(css):
    """
        Extract color definitions from CSS code.

        Currently limited to 6-digit hex values.
    """
    for colordef in re.finditer(r'color:\s*(#[0-9a-f]{6})', css):
        yield colordef[1]


def csscolors(url):
    """
        Main function.
    """
    style_extractor = StyleExtractor()
    style_extractor.feed(http_get(url), get_baseurl(url))

    colors = set()
    for style in style_extractor.stylesheets:
        colors.update(extract_colors(style))

    return sorted(colors, key=color_hex2hsv)


if __name__ == '__main__':
    print(*csscolors(argv[1]), sep='\n')
