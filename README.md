# csscolors
Script to extract color codes from CSS of websites.

No third-party dependencies.

## Usage
~~~
usage: csscolors.py [-h] [-c] [-t] [-s {rgb,hsl,occ}] URL

positional arguments:
  URL

options:
  -h, --help            show this help message and exit
  -c, --ansi-colors     colorize console output
  -t, --html-output     render colors as HTML table
  -s {rgb,hsl,occ}, --sort-by {rgb,hsl,occ}
                        sort colors by rgb values, hsl values or occurrence (default)
~~~

### Example

~~~
$ ./csscolors.py --sort-by hsl --html-output https://github.com > example/github-colors.html
$ more example/github-colors.html
<!doctype html>
<html><head><title>https://www.github.com</title></head>
<body><table style="font-family: monospace">
<tr><td align="right">18</td><td style="color: #FFFFFF; background-color: #000000"> #000000 &lt;Black&gt; </td><td> (0, 0, 0) </td></tr>
<tr><td align="right">1</td><td style="color: #FFFFFF; background-color: #060606"> #060606 </td><td> (6, 6, 6) </td></tr>
<tr><td align="right">1</td><td style="color: #FFFFFF; background-color: #404040"> #404040 </td><td> (64, 64, 64) </td></tr>
<tr><td align="right">3</td><td style="color: #FFFFFF; background-color: #555555"> #555555 </td><td> (85, 85, 85) </td></tr>
<tr><td align="right">3</td><td style="color: #000000; background-color: #999999"> #999999 </td><td> (153, 153, 153) </td></tr>
<tr><td align="right">1</td><td style="color: #000000; background-color: #dddddd"> #dddddd </td><td> (221, 221, 221) </td></tr>
<tr><td align="right">1</td><td style="color: #000000; background-color: #eeeeee"> #eeeeee </td><td> (238, 238, 238) </td></tr>
<tr><td align="right">1</td><td style="color: #000000; background-color: #f7f7f7"> #f7f7f7 </td><td> (247, 247, 247) </td></tr>
<tr><td align="right">16</td><td style="color: #000000; background-color: #ffffff"> #ffffff &lt;White&gt; </td><td> (255, 255, 255) </td></tr>
<tr><td align="right">1</td><td style="color: #FFFFFF; background-color: #aa2222"> #aa2222 </td><td> (170, 34, 34) </td></tr>
--More--
~~~
![github-colors.html](example/github-colors.png)
