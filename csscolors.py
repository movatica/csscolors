#!/usr/bin/env python3
"""
    csscolors.py

    Copyright (c) 2023 movatica <c0d3@movatica.com>
    Licensed under The MIT License (MIT)

    Extract, convert and display CSS color values used in a website.
    No third party dependencies.

    Usage:
        ./csscolors.py https://www.example.com/fromhere


TODO:
    - colored output on commandline
    - translate between all possible representations
        https://www.w3schools.com/cssref/css_colors_legal.php
    - add all representation variants to table
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


# Maps (R,G,B) tuple to color name.
# Source: https://www.w3schools.com/colors/colors_names.asp
RGB2ColorName = {
    (0, 0, 0): 'Black',
    (0, 0, 128): 'Navy',
    (0, 0, 139): 'DarkBlue',
    (0, 0, 205): 'MediumBlue',
    (0, 0, 255): 'Blue',
    (0, 100, 0): 'DarkGreen',
    (0, 128, 0): 'Green',
    (0, 128, 128): 'Teal',
    (0, 139, 139): 'DarkCyan',
    (0, 191, 255): 'DeepSkyBlue',
    (0, 206, 209): 'DarkTurquoise',
    (0, 250, 154): 'MediumSpringGreen',
    (0, 255, 0): 'Lime',
    (0, 255, 127): 'SpringGreen',
    (0, 255, 255): 'Cyan',
    (25, 25, 112): 'MidnightBlue',
    (30, 144, 255): 'DodgerBlue',
    (32, 178, 170): 'LightSeaGreen',
    (34, 139, 34): 'ForestGreen',
    (46, 139, 87): 'SeaGreen',
    (47, 79, 79): 'DarkSlateGrey',
    (50, 205, 50): 'LimeGreen',
    (60, 179, 113): 'MediumSeaGreen',
    (64, 224, 208): 'Turquoise',
    (65, 105, 225): 'RoyalBlue',
    (70, 130, 180): 'SteelBlue',
    (72, 61, 139): 'DarkSlateBlue',
    (72, 209, 204): 'MediumTurquoise',
    (75, 0, 130): 'Indigo',
    (85, 107, 47): 'DarkOliveGreen',
    (95, 158, 160): 'CadetBlue',
    (100, 149, 237): 'CornflowerBlue',
    (102, 51, 153): 'RebeccaPurple',
    (102, 205, 170): 'MediumAquaMarine',
    (105, 105, 105): 'DimGrey',
    (106, 90, 205): 'SlateBlue',
    (107, 142, 35): 'OliveDrab',
    (112, 128, 144): 'SlateGrey',
    (119, 136, 153): 'LightSlateGrey',
    (123, 104, 238): 'MediumSlateBlue',
    (124, 252, 0): 'LawnGreen',
    (127, 255, 0): 'Chartreuse',
    (127, 255, 212): 'Aquamarine',
    (128, 0, 0): 'Maroon',
    (128, 0, 128): 'Purple',
    (128, 128, 0): 'Olive',
    (128, 128, 128): 'Grey',
    (135, 206, 235): 'SkyBlue',
    (135, 206, 250): 'LightSkyBlue',
    (138, 43, 226): 'BlueViolet',
    (139, 0, 0): 'DarkRed',
    (139, 0, 139): 'DarkMagenta',
    (139, 69, 19): 'SaddleBrown',
    (143, 188, 143): 'DarkSeaGreen',
    (144, 238, 144): 'LightGreen',
    (147, 112, 219): 'MediumPurple',
    (148, 0, 211): 'DarkViolet',
    (152, 251, 152): 'PaleGreen',
    (153, 50, 204): 'DarkOrchid',
    (154, 205, 50): 'YellowGreen',
    (160, 82, 45): 'Sienna',
    (165, 42, 42): 'Brown',
    (169, 169, 169): 'DarkGrey',
    (173, 216, 230): 'LightBlue',
    (173, 255, 47): 'GreenYellow',
    (175, 238, 238): 'PaleTurquoise',
    (176, 196, 222): 'LightSteelBlue',
    (176, 224, 230): 'PowderBlue',
    (178, 34, 34): 'FireBrick',
    (184, 134, 11): 'DarkGoldenRod',
    (186, 85, 211): 'MediumOrchid',
    (188, 143, 143): 'RosyBrown',
    (189, 183, 107): 'DarkKhaki',
    (192, 192, 192): 'Silver',
    (199, 21, 133): 'MediumVioletRed',
    (205, 92, 92): 'IndianRed',
    (205, 133, 63): 'Peru',
    (210, 105, 30): 'Chocolate',
    (210, 180, 140): 'Tan',
    (211, 211, 211): 'LightGrey',
    (216, 191, 216): 'Thistle',
    (218, 112, 214): 'Orchid',
    (218, 165, 32): 'GoldenRod',
    (219, 112, 147): 'PaleVioletRed',
    (220, 20, 60): 'Crimson',
    (220, 220, 220): 'Gainsboro',
    (221, 160, 221): 'Plum',
    (222, 184, 135): 'BurlyWood',
    (224, 255, 255): 'LightCyan',
    (230, 230, 250): 'Lavender',
    (233, 150, 122): 'DarkSalmon',
    (238, 130, 238): 'Violet',
    (238, 232, 170): 'PaleGoldenRod',
    (240, 128, 128): 'LightCoral',
    (240, 230, 140): 'Khaki',
    (240, 248, 255): 'AliceBlue',
    (240, 255, 240): 'HoneyDew',
    (240, 255, 255): 'Azure',
    (244, 164, 96): 'SandyBrown',
    (245, 222, 179): 'Wheat',
    (245, 245, 220): 'Beige',
    (245, 245, 245): 'WhiteSmoke',
    (245, 255, 250): 'MintCream',
    (248, 248, 255): 'GhostWhite',
    (250, 128, 114): 'Salmon',
    (250, 235, 215): 'AntiqueWhite',
    (250, 240, 230): 'Linen',
    (250, 250, 210): 'LightGoldenRodYellow',
    (253, 245, 230): 'OldLace',
    (255, 0, 0): 'Red',
    (255, 0, 255): 'Magenta',
    (255, 20, 147): 'DeepPink',
    (255, 69, 0): 'OrangeRed',
    (255, 99, 71): 'Tomato',
    (255, 105, 180): 'HotPink',
    (255, 127, 80): 'Coral',
    (255, 140, 0): 'DarkOrange',
    (255, 160, 122): 'LightSalmon',
    (255, 165, 0): 'Orange',
    (255, 182, 193): 'LightPink',
    (255, 192, 203): 'Pink',
    (255, 215, 0): 'Gold',
    (255, 218, 185): 'PeachPuff',
    (255, 222, 173): 'NavajoWhite',
    (255, 228, 181): 'Moccasin',
    (255, 228, 196): 'Bisque',
    (255, 228, 225): 'MistyRose',
    (255, 235, 205): 'BlanchedAlmond',
    (255, 239, 213): 'PapayaWhip',
    (255, 240, 245): 'LavenderBlush',
    (255, 245, 238): 'SeaShell',
    (255, 248, 220): 'Cornsilk',
    (255, 250, 205): 'LemonChiffon',
    (255, 250, 240): 'FloralWhite',
    (255, 250, 250): 'Snow',
    (255, 255, 0): 'Yellow',
    (255, 255, 224): 'LightYellow',
    (255, 255, 240): 'Ivory',
    (255, 255, 255): 'White',
}

# Maps color name to (R,G,B) tuple.
# Source: https://www.w3schools.com/colors/colors_names.asp
ColorName2RGB = {
    'aliceblue': (240, 248, 255),
    'antiquewhite': (250, 235, 215),
    'aqua': (0, 255, 255),
    'aquamarine': (127, 255, 212),
    'azure': (240, 255, 255),
    'beige': (245, 245, 220),
    'bisque': (255, 228, 196),
    'black': (0, 0, 0),
    'blanchedalmond': (255, 235, 205),
    'blue': (0, 0, 255),
    'blueviolet': (138, 43, 226),
    'brown': (165, 42, 42),
    'burlywood': (222, 184, 135),
    'cadetblue': (95, 158, 160),
    'chartreuse': (127, 255, 0),
    'chocolate': (210, 105, 30),
    'coral': (255, 127, 80),
    'cornflowerblue': (100, 149, 237),
    'cornsilk': (255, 248, 220),
    'crimson': (220, 20, 60),
    'cyan': (0, 255, 255),
    'darkblue': (0, 0, 139),
    'darkcyan': (0, 139, 139),
    'darkgoldenrod': (184, 134, 11),
    'darkgray': (169, 169, 169),
    'darkgreen': (0, 100, 0),
    'darkgrey': (169, 169, 169),
    'darkkhaki': (189, 183, 107),
    'darkmagenta': (139, 0, 139),
    'darkolivegreen': (85, 107, 47),
    'darkorange': (255, 140, 0),
    'darkorchid': (153, 50, 204),
    'darkred': (139, 0, 0),
    'darksalmon': (233, 150, 122),
    'darkseagreen': (143, 188, 143),
    'darkslateblue': (72, 61, 139),
    'darkslategray': (47, 79, 79),
    'darkslategrey': (47, 79, 79),
    'darkturquoise': (0, 206, 209),
    'darkviolet': (148, 0, 211),
    'deeppink': (255, 20, 147),
    'deepskyblue': (0, 191, 255),
    'dimgray': (105, 105, 105),
    'dimgrey': (105, 105, 105),
    'dodgerblue': (30, 144, 255),
    'firebrick': (178, 34, 34),
    'floralwhite': (255, 250, 240),
    'forestgreen': (34, 139, 34),
    'fuchsia': (255, 0, 255),
    'gainsboro': (220, 220, 220),
    'ghostwhite': (248, 248, 255),
    'gold': (255, 215, 0),
    'goldenrod': (218, 165, 32),
    'gray': (128, 128, 128),
    'green': (0, 128, 0),
    'greenyellow': (173, 255, 47),
    'grey': (128, 128, 128),
    'honeydew': (240, 255, 240),
    'hotpink': (255, 105, 180),
    'indianred': (205, 92, 92),
    'indigo': (75, 0, 130),
    'ivory': (255, 255, 240),
    'khaki': (240, 230, 140),
    'lavender': (230, 230, 250),
    'lavenderblush': (255, 240, 245),
    'lawngreen': (124, 252, 0),
    'lemonchiffon': (255, 250, 205),
    'lightblue': (173, 216, 230),
    'lightcoral': (240, 128, 128),
    'lightcyan': (224, 255, 255),
    'lightgoldenrodyellow': (250, 250, 210),
    'lightgray': (211, 211, 211),
    'lightgreen': (144, 238, 144),
    'lightgrey': (211, 211, 211),
    'lightpink': (255, 182, 193),
    'lightsalmon': (255, 160, 122),
    'lightseagreen': (32, 178, 170),
    'lightskyblue': (135, 206, 250),
    'lightslategray': (119, 136, 153),
    'lightslategrey': (119, 136, 153),
    'lightsteelblue': (176, 196, 222),
    'lightyellow': (255, 255, 224),
    'lime': (0, 255, 0),
    'limegreen': (50, 205, 50),
    'linen': (250, 240, 230),
    'magenta': (255, 0, 255),
    'maroon': (128, 0, 0),
    'mediumaquamarine': (102, 205, 170),
    'mediumblue': (0, 0, 205),
    'mediumorchid': (186, 85, 211),
    'mediumpurple': (147, 112, 219),
    'mediumseagreen': (60, 179, 113),
    'mediumslateblue': (123, 104, 238),
    'mediumspringgreen': (0, 250, 154),
    'mediumturquoise': (72, 209, 204),
    'mediumvioletred': (199, 21, 133),
    'midnightblue': (25, 25, 112),
    'mintcream': (245, 255, 250),
    'mistyrose': (255, 228, 225),
    'moccasin': (255, 228, 181),
    'navajowhite': (255, 222, 173),
    'navy': (0, 0, 128),
    'oldlace': (253, 245, 230),
    'olive': (128, 128, 0),
    'olivedrab': (107, 142, 35),
    'orange': (255, 165, 0),
    'orangered': (255, 69, 0),
    'orchid': (218, 112, 214),
    'palegoldenrod': (238, 232, 170),
    'palegreen': (152, 251, 152),
    'paleturquoise': (175, 238, 238),
    'palevioletred': (219, 112, 147),
    'papayawhip': (255, 239, 213),
    'peachpuff': (255, 218, 185),
    'peru': (205, 133, 63),
    'pink': (255, 192, 203),
    'plum': (221, 160, 221),
    'powderblue': (176, 224, 230),
    'purple': (128, 0, 128),
    'rebeccapurple': (102, 51, 153),
    'red': (255, 0, 0),
    'rosybrown': (188, 143, 143),
    'royalblue': (65, 105, 225),
    'saddlebrown': (139, 69, 19),
    'salmon': (250, 128, 114),
    'sandybrown': (244, 164, 96),
    'seagreen': (46, 139, 87),
    'seashell': (255, 245, 238),
    'sienna': (160, 82, 45),
    'silver': (192, 192, 192),
    'skyblue': (135, 206, 235),
    'slateblue': (106, 90, 205),
    'slategray': (112, 128, 144),
    'slategrey': (112, 128, 144),
    'snow': (255, 250, 250),
    'springgreen': (0, 255, 127),
    'steelblue': (70, 130, 180),
    'tan': (210, 180, 140),
    'teal': (0, 128, 128),
    'thistle': (216, 191, 216),
    'tomato': (255, 99, 71),
    'turquoise': (64, 224, 208),
    'violet': (238, 130, 238),
    'wheat': (245, 222, 179),
    'white': (255, 255, 255),
    'whitesmoke': (245, 245, 245),
    'yellow': (255, 255, 0),
    'yellowgreen': (154, 205, 50)
}


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
            url = next((v for k,v in attrs if k == 'href'), '')

            if url:
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


class Color:
    """ Encapsulate CSS color values including conversion. """
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __eq__(self, other):
        return (self.red, self.green, self.blue) == (other.red, other.green, other.blue)

    def __hash__(self):
        """ Hash over RGB value """
        return self.red * 256 * 256 + self.blue * 256 + self.green

    def __lt__(self, other):
        """ Default sorting by RGB value """
        return (self.red, self.green, self.blue) < (other.red, other.green, other.blue)

    def __str__(self):
        """ Default representation is the hex string """
        return self.to_hexstr()

    def get_bwcontrast(self):
        """ Approximate whether black or white has better contrast. """
        luminosity = 2*self.red + 7*self.green + self.blue

        return Color(255,255,255) if luminosity < 5*255 else Color(0,0,0)

    def get_name(self):
        """ Get color name if present. """
        try:
            return RGB2ColorName[(self.red, self.green, self.blue)]
        except KeyError:
            return ''

    def is_known(self):
        """ Return whether the color value matches a predefined name. """
        return (self.red, self.green, self.blue) in RGB2ColorName

    def to_hexstr(self):
        """ Return hex representation. """
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    def to_rgb(self):
        """ Return rgb function representation. """
        return (self.red, self.green, self.blue)

    def to_rgbstr(self):
        """ Return rgb function representation. """
        return f"rgb({self.red}, {self.green}, {self.blue})"

    def to_hsl(self):
        """ Convert to HSL tuple. """
        red, grn, blu = self.red, self.green, self.blue

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

    def to_hslstr(self):
        """ Return hsl function representation. """
        return "hsl({}, {}, {})".format(*self.to_hsl())


    @classmethod
    def from_hexstr(cls, hexstr):
        """ Factory function from hex string. Raises ValueError on invalid string. """

        if len(hexstr) >= 6:
            return cls(int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16))

        if len(hexstr) >= 3:
            return cls(int(hexstr[0], 16) * 0x11, int(hexstr[1], 16) * 0x11, int(hexstr[2], 16) * 0x11)

        raise ValueError


    @classmethod
    def from_name(cls, name):
        """ Factory function from well known name. Raises KeyError on invalid name. """

        return cls(*ColorName2RGB[name])



def http_get(url, baseurl = ''):
    """
        Return content and url from webpage using urlopen.

        Returning of the reponse url is necessary to handle redirects.
    """

    request = Request(
        url=urljoin(baseurl, url),
        data=None,
        headers={
            'Accept': 'text/*',
            'Referer': baseurl,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        })

    retry = 2
    while retry:
        try:
            retry -= 1
            response = urlopen(request, timeout = 10)
            return response.read().decode('utf-8'), response.url
        except (URLError, UnicodeError) as err:
            print(f"{err} <{request.full_url}>", file=stderr)

    return '', ''


def find_colors(css):
    """
        Extract color definitions from CSS code.

        Currently limited to hex values and names.
    """
    for colordef in re.finditer(r'color:\s*#([0-9a-f]{3,6})', css):
        yield Color.from_hexstr(colordef[1])

    for colordef in re.finditer(r'color:\s*([A-Za-z]{3,20})', css):
        try:
            yield Color.from_name(colordef[1].lower())
        except KeyError:
            continue


def read_arguments():
    """ Read commandline arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('URL', type=lambda u: Request(u).full_url)
    parser.add_argument('--html-output', action='store_true',
            help='render colors as HTML table')
    parser.add_argument('--sort-by', choices=['rgb', 'hsl', 'occ'], default='occ',
            help='sort colors by rgb values, hsl values or occurrence (default)')
    return parser.parse_args()


def csscolors(url):
    """ Main function. """

    style_extractor = StyleExtractor()

    style_extractor.feed(*http_get(url, url))

    colors = Counter()
    for style in style_extractor.stylesheets:
        colors.update(find_colors(style))

    return colors


def html_table(colorlist, title):
    """ Render list of colors as html table. """

    lines = [
            '<!doctype html>',
            '<html><head><title>'+html.escape(title)+'</title></head>',
            '<body><table style="font-family: monospace">'
            ]

    for color, occurrence in colorlist:
        name = f' &lt;{color.get_name()}&gt;' if color.is_known() else ''

        lines.append('<tr>'
                f'<td align="right">{occurrence}</td>'
                f'<td style="color: {color.get_bwcontrast()};'
                    f' background-color: {color}">'
                    f' {color}{name} </td>'
                f'<td> {color.to_rgbstr()} </td>'
                 '</tr>')

    lines.append('</table></body></html>')

    return lines


if __name__ == '__main__':
    argv = read_arguments()
    colors = csscolors(argv.URL)

    if argv.sort_by == 'rgb':
        result = sorted(colors.items())
    elif argv.sort_by == 'hsl':
        result = sorted(colors.items(), key=lambda c:c.to_hsl())
    else: # argv.sort_by == 'occ'
        result = colors.most_common()

    if argv.html_output:
        lines = html_table(result, argv.URL)
    else:
        lines = [f'{occurence}\t{color.to_rgbstr()}' for color, occurence in result]

    print(*lines, sep='\n')
