# `tslogs` [![Stars](https://img.shields.io/github/stars/ashutoshvarma/tslogs.svg?style=social&maxAge=3600&label=Star)](https://github.com/ashutoshvarma/tslogs/stargazers)
*A Python parser and visualizer for ThrottleStop logs.*

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/ashutoshvarma/tslogs/Python%20package/main?style=flat-square)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square&maxAge=2678400)](https://choosealicense.com/licenses/mit/)
[![Source](https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=2678400&style=flat-square)](https://github.com/ashutoshvarma/tslogs/)
[![Coverage](https://img.shields.io/codecov/c/gh/ashutoshvarma/tslogs?style=flat-square&maxAge=3600)](https://codecov.io/gh/ashutoshvarma/tslogs/)
[![PyPI](https://img.shields.io/pypi/v/tslogs.svg?style=flat-square&maxAge=3600)](https://pypi.python.org/pypi/tslogs)
[![Versions](https://img.shields.io/pypi/pyversions/tslogs.svg?style=flat-square&maxAge=3600)](https://pypi.org/project/tslogs/#files)
[![Wheel](https://img.shields.io/pypi/wheel/pronto?style=flat-square&maxAge=3600)](https://pypi.org/project/pronto/#files)
[![GitHub issues](https://img.shields.io/github/issues/ashutoshvarma/tslogs.svg?style=flat-square&maxAge=600)](https://github.com/ashutoshvarma/tslogs/issues)
[![Downloads](https://img.shields.io/badge/dynamic/json?style=flat-square&color=303f9f&maxAge=86400&label=downloads&query=%24.total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2Ftslogs)](https://pepy.tech/project/tslogs)

## 🚩 Table of Contents

- [Overview](#%EF%B8%8F-overview)
  - [What is ThrottleStop ?](#-what-is-throttlestop-)
  - [Why would you like to parse ThrottleStop Logs ?](#why-would-you-like-to-parse-throttlestop-logs-)
  - [Enable Logging in ThrottleStop](#%EF%B8%8F-enable-logging-in-throttlestop)
- [Installing](#-installing)
- [Usage](#-usage)
- [License](#-license)



## 🗺️ Overview

tslogs is a Python library to parse, browse, export and visualize
[ThrottleStop](https://www.techpowerup.com/download/techpowerup-throttlestop/) log files.

#### 📖 What is ThrottleStop ?
> [ThrottleStop](https://www.techpowerup.com/download/techpowerup-throttlestop/)
is a small application designed to monitor for 
and correct the three main types of CPU throttling that are 
being used on many laptop computers.

Official Thread - [here](http://forum.notebookreview.com/threads/the-throttlestop-guide.531329/)

Comprehensive Guide - [here](https://www.ultrabookreview.com/31385-the-throttlestop-guide/)

#### Why would you like to parse ThrottleStop Logs ?
TODO

#### 🏳️ Enable Logging in ThrottleStop
<table>
  <tr>
    <td>Select the `Log File` checkbox</td>
     <td>Click on `Options` button and Select the Folder where you want logs to be saved.</td>
  </tr>
  <tr>
    <td valign="top">
      <img src="https://github.com/ashutoshvarma/tslogs/blob/main/docs/_static/throttlestop-log-enable.jpg?raw=true" width="500" height="400">
    </td>
    <td valign="top">
      <img src="https://github.com/ashutoshvarma/tslogs/blob/main/docs/_static/throttlestop-log-folder.jpg?raw=true" width="500" height="400">
    </td>
  </tr>
 </table>
 
## 🔧 Installing

Installing with `pip` is the easiest:
```console
# pip install tslogs          # if you have the admin rights
$ pip install tslogs --user   # install it in a user-site directory
```

Finally, a development version can be installed from GitHub
using `setuptools` & `pip`
```console
$ git clone https://github.com/ashutoshvarma/tslogs
$ cd tslogs
# pip install .
```

## 💡 Usage 
### 1. `tslogs` - CLI tool
```console
$ tslogs --help
usage: tslogs [-h] [--json | --plot ] [--dates START END] [--interval INTERVAL] [--smooth SMOOTH] [--output FILE] [--indent VALUE] [--quiet]
              [--version]
              paths paths

positional arguments:
  paths                 One or more paths to log dir or log files.

optional arguments:
  -h, --help            show this help message and exit
  --json, -j            dump all parsed log data.
  --plot, -p            Plot given the logs attributes (default: None). Allowed values are {multi, c0, clock_mod, chip_mod, battery_mw,       
                        cpu_temp, gpu_mhz, gpu_temp, vid, power}
  --quiet, -q           Run in silent mode
  --version, -v         show program's version number and exit

Filter:
  --dates, -d START END
                        Datetime range to filter (in ISO format, yyyy-mm-dd HH:MM:SS)

Plot Options:
  --interval, -I INTERVAL
                        Plot data frequency in seconds (default: 60)
  --smooth, -S SMOOTH   Span interval for smoothing the graph, if data frequency is very high using increasing this with 'interval' can       
                        yield smooth graph (default: 2)

Output:
  --output, -o FILE     Output file path, default is '-' (stdout)
  --indent VALUE        indent value for json output, default is 4
```
- #### a.) Print the summary
  ![tslogs-summary](docs/_static/summary.jpg)

- #### b.) Plot Graphs
  This will plot `cpu_temp`, `multi` (clock speed in GHz),
  `power` (in W) and `c0` from logs between time 16:00 to 16:15 in `2020-07-28.txt` 
  ```console
  tslogs .\tests\logs\2020-07-28.txt -p cpu_temp multi power --smooth 2 --interval 1 -d "2020-07-28 16:00:00" "2020-07-28 16:15:00"
  ```
  ![tslogs-plot](docs/_static/plot.jpg)

### 2. `tslogs` - Python Module
TODO

See `parse_logs()` and `LogLine` in `parse.py`. For more references
see the CLI implementation in `cli.py`



## 📜 License

This library is provided under the open-source
[MIT license](https://choosealicense.com/licenses/mit/).
