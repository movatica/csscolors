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
$ ./csscolors.py --sort-by hsl --html-output https://github.com | tee example/github-colors.html 
<!doctype html>
<html><head>
<title>https://github.com</title>
<style>
td { padding-top: 2px; padding-bottom: 2px; padding-left: 4px; padding-right: 4px; }
body { font-family: monospace; }
</style></head>
<body><table>
<tr style="color: #ffffff; background-color: #000000"><td align="right"> 22 </td><td> Black </td><td> #000000 </td><td> rgb(0, 0, 0) </td><td> hsl(0, 0%, 0%) </td></tr>
<tr style="color: #ffffff; background-color: #060606"><td align="right"> 1 </td><td>  </td><td> #060606 </td><td> rgb(6, 6, 6) </td><td> hsl(0, 0%, 2%) </td></tr>
<tr style="color: #ffffff; background-color: #404040"><td align="right"> 1 </td><td>  </td><td> #404040 </td><td> rgb(64, 64, 64) </td><td> hsl(0, 0%, 25%) </td></tr>
<tr style="color: #ffffff; background-color: #555555"><td align="right"> 3 </td><td>  </td><td> #555555 </td><td> rgb(85, 85, 85) </td><td> hsl(0, 0%, 33%) </td></tr>
<tr style="color: #000000; background-color: #999999"><td align="right"> 3 </td><td>  </td><td> #999999 </td><td> rgb(153, 153, 153) </td><td> hsl(0, 0%, 60%) </td></tr>
<tr style="color: #000000; background-color: #dddddd"><td align="right"> 1 </td><td>  </td><td> #dddddd </td><td> rgb(221, 221, 221) </td><td> hsl(0, 0%, 87%) </td></tr>
<tr style="color: #000000; background-color: #eeeeee"><td align="right"> 1 </td><td>  </td><td> #eeeeee </td><td> rgb(238, 238, 238) </td><td> hsl(0, 0%, 93%) </td></tr>
<tr style="color: #000000; background-color: #f7f7f7"><td align="right"> 1 </td><td>  </td><td> #f7f7f7 </td><td> rgb(247, 247, 247) </td><td> hsl(0, 0%, 97%) </td></tr>
<tr style="color: #000000; background-color: #ffffff"><td align="right"> 9 </td><td> White </td><td> #ffffff </td><td> rgb(255, 255, 255) </td><td> hsl(0, 0%, 100%) </td></tr>
<tr style="color: #ffffff; background-color: #aa2222"><td align="right"> 1 </td><td>  </td><td> #aa2222 </td><td> rgb(170, 34, 34) </td><td> hsl(0, 67%, 40%) </td></tr>
[...]
~~~
![github-colors.html](example/github-colors.png)
