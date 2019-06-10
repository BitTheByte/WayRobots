from colorama import Fore, init
import argparse
import requests
import time
import re

init(autoreset=True)
log = ""


def pprint(out):
    global log
    log += out + "\n"

    out = " " + out
    if "[ERROR]" in out:
        out = out.replace("[ERROR]", "[%sERROR%s]" % (Fore.RED, Fore.RESET))

    if "[WARNING]" in out:
        out = out.replace("[WARNING]", "[%sWARNING]%s" % (Fore.LIGHTWHITE_EX, Fore.YELLOW))

    if "[robots.txt]" in out:
        out = out.replace("[robots.txt]", "[%srobots.txt%s]" % (Fore.LIGHTBLACK_EX, Fore.RESET))

    if "|_->" in out:
        out = out.replace("->", "->%s" % (Fore.LIGHTBLUE_EX))

    if "|_-->" in out:
            if ":   200" in out:
                out = out.replace("|_-->", "%s|_-->%s" % (Fore.LIGHTGREEN_EX, Fore.GREEN))
            elif ":   30" in out:
                out = out.replace("|_-->", "%s|_-->%s" % (Fore.LIGHTGREEN_EX, Fore.YELLOW))
            else:
                out = out.replace("|_-->", "%s|_-->%s" % (Fore.LIGHTGREEN_EX, Fore.RED))

    if "*-" in out:
        out = out.replace("*-", "%s*%s-%s" % (Fore.BLUE, Fore.RED, Fore.LIGHTWHITE_EX))

    if ":[" in out:
        out = out.replace(":[", ":[%s" % Fore.LIGHTRED_EX)
        out = out.replace("]", "%s]" % Fore.WHITE)
    print(out)


def parse_robots(txt):
    txt = txt.split("\n")
    res = []
    for line in txt:
        if not "#" in line:
            if ":" in line and "/" in line and not "http" in line:
                res.append(line.split(":")[1].strip())
    return res


def fetch_content(ts, target):
    ts_dirs = []
    for timestap in ts:
        try:
            content = requests.get("http://web.archive.org/web/{}if_/{}".format(timestap, target)).content
            dirs = parse_robots(content)
            ts_dirs.append({timestap: dirs})
        except:
            pass
    return ts_dirs



def wayback_find_robots(host):
    content = requests.get(
        "http://web.archive.org/cdx/m_search/cdx?url=*.{}/*&output=txt&fl=original&collapse=urlkey".format(
            host)).content
    robots_files = re.findall(r".*?.%s.*/robots\.txt" % host, content)
    return robots_files


def wayback_url(url, year):
    allowed_statuses = [200]
    try:
        result = requests.get(
            "http://web.archive.org/__wb/calendarcaptures?url={}&selected_year={}".format(url, year)).json()
    except:
        return

    for month in range(0, 12):

        m_search = result[month]
        weeks = len(m_search)
        current_day = 0

        for days in range(weeks):
            for day in m_search[days]:

                if day != None:
                    current_day += 1

                    if day != {}:
                        ts = day['ts']
                        st = day['st'][0]

                        if st in allowed_statuses:
                            timestamp2dir = fetch_content(ts, url)

                            for i in timestamp2dir:
                                for ts, val in i.items():
                                    yield ts, val


def check_endpoint_stat(endpoint):
    request = requests.head(endpoint)
    return request.status_code


def crawling_robots(endpoint):
    if '.' in endpoint:
        endpoint = endpoint.split('.')[0] + '\\.' + endpoint.split('.')[1]
    if '*' in endpoint:
        _tmp = [_temp.start() for _temp in re.finditer(r'\*', endpoint)]
        temp = endpoint[0:_tmp[0]]
        for i in range(len(_tmp)):
            if i in range(len(_tmp) - 1):
                temp = temp + "." + endpoint[_tmp[i]:_tmp[i+1]]
            else:
                temp = temp + "." + endpoint[_tmp[i]:len(endpoint)]
                endpoint = ".*" + temp + ".*"
    else:
        endpoint = ".*" + endpoint + ".*"
    content = requests.get(
        "http://web.archive.org/cdx/search/cdx?url={}&matchType=prefix&from=2016&to=2018&output=txt&collapse=urlkey&fl=original".format(target)).content
    wp_files = re.findall(endpoint, content)
    return wp_files


parser = argparse.ArgumentParser(description='Welcome to domainker help page')
parser.add_argument('-i', '--input', type=str, help='Target host')
parser.add_argument('-o', '--output', type=str, help='Output file')
parser.add_argument('-y', '--year', type=str, help='Years Range e.g[2014-2019]')
args = parser.parse_args()

if not args.input:
    pprint("[ERROR] Please specify the target first using -i")
    exit()

if not args.year:
    pprint("[WARNING] You haven't specify the year, Using current year: %s" % time.strftime("%Y"))
    args.year = "%s-%s" % (time.strftime("%Y"), time.strftime("%Y"))

if not "-" in args.year:
    pprint("[ERROR] Please specify starting and ending year e.g[2014-2019]")
    exit()

year = args.year
target = args.input

pprint("Searching for robots.txt on *.%s" % target)

robots_txt = set(wayback_find_robots(target))

if len(robots_txt) == 0:
    pprint("[ERROR] Wasn't able to find any [robots.txt] files")
    exit()

pprint("Found [robots.txt] on the following:\n\n  *- " + '\n  *- '.join(robots_txt) + "\n")

year_from = int(year.split("-")[0])
year_to = int(year.split("-")[1])

for year in range(year_from, year_to + 1):
    for robot_file in robots_txt:
        pprint("[%s]::[%s] Searching for [robots.txt] snapshot" % (year, robot_file))
        wb = wayback_url(robot_file, year)

        _tmp = []
        for result in wb:
            for dir_name in result[1]:
                if dir_name not in _tmp:
                    pprint("  |_-> " + dir_name)
                    if dir_name != "/":
                        for i in range(len(crawling_robots(dir_name))):
                            pprint("         |_--> " + crawling_robots(dir_name)[i] + "    :   " + str(check_endpoint_stat(crawling_robots(dir_name)[i])))
                _tmp.append(dir_name)

if args.output:
    open(args.output, "w").write(log)