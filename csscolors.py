#!/usr/bin/env python3
"""
    csscolors.py

    Copyright (c) 2023 movatica <c0d3@movatica.com>
    Licensed under The MIT License (MIT)

    Extract all color codes used in CSS in a website, reasonably sorted by HSV.
    No third party dependencies.

    Usage:
        ./csscolors.py https://www.example.com/fromhere


TODO:
    - support all possible CSS color values
        i.e. hex, hexa, rgb, rgba, hsl, hsla, named
    - print colored output and more info about colors
        i.e. assign names to known colors, rgb/hsv table, ...
    - add filtering options
        i.e. minimal count, ranges for hsv, ...
"""

import argparse
from collections import Counter
import html
from html.parser import HTMLParser
import re
from sys import stderr
from urllib.error import URLError
from urllib.parse import urljoin
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
                css, _ = http_get(url, self.baseurl)

        else:
            css = next((v for k,v in attrs if k == 'style'), '')

        if css:
            self.stylesheets.append(css)

    def handle_endtag(self, tag):
        self.styledata = False

    def handle_data(self, data):
        if self.styledata:
            self.stylesheets.append(data)


def http_get(url, baseurl = ''):
    """
        Return content and url from webpage using urlopen.

        Returning of the reponse url is necessary to handle redirects.
    """

    request = Request(
        urljoin(baseurl, url),
        data=None,
        headers={
            # Circumvent blocking of scripts on some sites.
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0',
            'Referer': baseurl
        })

    try:
        with urlopen(request) as response:
            return response.read().decode('utf-8'), response.url
    except URLError as err:
        print(err, file=stderr)
        return '', ''


def color_hex2rgb(hexstr):
    """ Convert a css color hex string to RGB. Returns a tuple of integers (r,g,b)."""

    if len(hexstr) >= 6:
        return int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16)

    if len(hexstr) >= 3:
        return int(hexstr[0], 16) * 0x11, int(hexstr[1], 16) * 0x11, int(hexstr[2], 16) * 0x11

    raise ValueError


def color_hex2hsl(hexstr):
    """ Convert a six-digit hexvalue to HSV. Returns a tuple of integers (h,s,v)."""

    red, grn, blu = color_hex2rgb(hexstr)

    red /= 255.0
    grn /= 255.0
    blu /= 255.0

    val = max(red, grn, blu)
    xmin = min(red, grn, blu)
    crm = val - xmin

    lit = (val + xmin) / 2.0


    hue = 60
    if crm == 0.0:
        hue = 0
    elif val == red:
        hue *= ((grn - blu) / crm) % 6
    elif val == grn:
        hue *= ((blu - red) / crm) + 2
    elif val == blu:
        hue *= ((red - grn) / crm) + 4

    sat = 0
    if 0.0 < lit < 1.0:
        sat = (val - lit) / min(lit, 1.0-lit)

    return hue, sat, lit


def find_colors(css):
    """
        Extract color definitions from CSS code.

        Currently limited to hex values.
    """
    for colordef in re.finditer(r'color:\s*#([0-9a-f]{3,})', css):
        yield colordef[1]


def read_arguments():
    """ Read commandline arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('URL', type=lambda u: Request(u).full_url)
    parser.add_argument('--html-output', action='store_true',
            help='render colors as HTML table')
    parser.add_argument('--sort-by', choices=['rgb', 'hsl', 'occ'], default='rgb',
            help='sort colors by rgb value (default), hsl value or occurrence')
    return parser.parse_args()


def csscolors(url, sortby):
    """ Main function. """

    style_extractor = StyleExtractor()

    style_extractor.feed(*http_get(url))

    colors = Counter()
    for style in style_extractor.stylesheets:
        colors.update(find_colors(style))

    if sortby == 'rgb':
        return sorted(colors.keys())
    elif sortby == 'hsl':
        return sorted(colors.keys(), key=color_hex2hsl)
    else: # sortby == 'occ'
        return (color for color,_ in colors.most_common())


def html_table(colorlist, title):
    """ Render list of colors as html table. """

    lines = [
            '<!doctype html>',
            '<html><head><title>'+html.escape(title)+'</title></head>',
            '<body><table style="font-family: monospace">'
            ]

    for color in colorlist:
        lines.append('<tr>'
                '<td style="background-color: '+color+'"> '+color+' </td>'
                '<td> '+str(color_hex2rgb(color))+' </td>'
                '</tr>')

    lines.append('</table></body></html>')

    return lines


if __name__ == '__main__':
    argv = read_arguments()
    result = csscolors(argv.URL, argv.sort_by)

    if argv.html_output:
        result = html_table(result, argv.URL)

    print(*result, sep='\n')
