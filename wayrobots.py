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

    out = f" {out}"
    if "[ERROR]" in out:
        out = out.replace("[ERROR]", f"[{Fore.RED}ERROR{Fore.RESET}]")

    if "[WARNING]" in out:
        out = out.replace("[WARNING]", f"[{Fore.LIGHTWHITE_EX}WARNING]{Fore.YELLOW}")

    if "[robots.txt]" in out:
        out = out.replace(
            "[robots.txt]", f"[{Fore.LIGHTBLACK_EX}robots.txt{Fore.RESET}]"
        )

    if "|_->" in out:
        out = out.replace("->", f"->{Fore.LIGHTBLUE_EX}")

    if "|_-->" in out:
        if ":   200" in out:
            out = out.replace("|_-->", f"{Fore.LIGHTGREEN_EX}|_-->{Fore.GREEN}")
        elif ":   30" in out:
            out = out.replace("|_-->", f"{Fore.LIGHTGREEN_EX}|_-->{Fore.YELLOW}")
        else:
            out = out.replace("|_-->", f"{Fore.LIGHTGREEN_EX}|_-->{Fore.RED}")

    if "*-" in out:
        out = out.replace("*-", f"{Fore.BLUE}*{Fore.RED}-{Fore.LIGHTWHITE_EX}")

    if ":[" in out:
        out = out.replace(":[", f":[{Fore.LIGHTRED_EX}")
        out = out.replace("]", f"{Fore.WHITE}]")
    if "=>" in out:
        out = out.replace(
            "=>", f"{Fore.LIGHTBLACK_EX}={Fore.RED}>{Fore.LIGHTWHITE_EX}"
        )
    print(out)


def parse_robots(txt):
    txt = txt.split("\n")
    res = []
    for line in txt:
        if "#" not in line:
            if ":" in line and "/" in line and "http" not in line:
                res.append(line.split(":")[1].strip())
    return res


def fetch_content(ts, target):
    ts_dirs = []
    for timestap in ts:
        try:
            content = requests.get(
                f"http://web.archive.org/web/{timestap}if_/{target}"
            ).content
            dirs = parse_robots(content)
            ts_dirs.append({timestap: dirs})
        except:
            pass
    return ts_dirs



def wayback_find_robots(host):
    content = requests.get(
        f"http://web.archive.org/cdx/m_search/cdx?url=*.{host}/*&output=txt&fl=original&collapse=urlkey"
    ).content
    return re.findall(r".*?.%s.*/robots\.txt" % host, content)


def wayback_url(url, year):
    allowed_statuses = [200]
    try:
        result = requests.get(
            f"http://web.archive.org/__wb/calendarcaptures?url={url}&selected_year={year}"
        ).json()
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
                        st = day['st'][0]

                        if st in allowed_statuses:
                            ts = day['ts']
                            timestamp2dir = fetch_content(ts, url)

                            for i in timestamp2dir:
                                yield from i.items()


def check_endpoint_stat(endpoint):
    request = requests.head(endpoint)
    return request.status_code


def crawling_robots(endpoint):
    if '.' in endpoint:
        endpoint = endpoint.split('.')[0] + '\\.' + endpoint.split('.')[1]
    if '*' in endpoint:
        _tmp = [_temp.start() for _temp in re.finditer(r'\*', endpoint)]
        temp = endpoint[:_tmp[0]]
        for i in range(len(_tmp)):
            if i in range(len(_tmp) - 1):
                temp = f"{temp}.{endpoint[_tmp[i]:_tmp[i + 1]]}"
            else:
                temp = f"{temp}.{endpoint[_tmp[i]:]}"
                endpoint = f".*{temp}.*"
    else:
        endpoint = f".*{endpoint}.*"
    content = requests.get(
        f"http://web.archive.org/cdx/search/cdx?url={target}&matchType=prefix&from={year_from}&to={year_to}&output=txt&collapse=urlkey&fl=original"
    ).content
    return re.findall(endpoint, content)


parser = argparse.ArgumentParser(description='Welcome to domainker help page')
parser.add_argument('-i', '--input', type=str, help='Target host')
parser.add_argument('-o', '--output', type=str, help='Output file')
parser.add_argument('-y', '--year', type=str, help='Years Range e.g[2014-2019]')
args = parser.parse_args()

if not args.input:
    pprint("[ERROR] Please specify the target first using -i")
    exit()

if not args.year:
    pprint(
        f"""[WARNING] You haven't specify the year, Using current year: {time.strftime("%Y")}"""
    )
    args.year = f'{time.strftime("%Y")}-{time.strftime("%Y")}'

if "-" not in args.year:
    pprint("[ERROR] Please specify starting and ending year e.g[2014-2019]")
    exit()

year = args.year
target = args.input

pprint(f"Searching for robots.txt on *.{target}")

robots_txt = set(wayback_find_robots(target))

if not robots_txt:
    pprint("[ERROR] Wasn't able to find any [robots.txt] files")
    exit()

pprint("Found [robots.txt] on the following:\n\n  *- " + '\n  *- '.join(robots_txt) + "\n")

year_from = int(year.split("-")[0])
year_to = int(year.split("-")[1])

for year in range(year_from, year_to + 1):
    for robot_file in robots_txt:
        pprint(f"[{year}]::[{robot_file}] Searching for [robots.txt] snapshot")
        wb = wayback_url(robot_file, year)

        _tmp = []
        for result in wb:
            for dir_name in result[1]:
                if dir_name not in _tmp:
                    pprint(f"  |_-> {dir_name}")
                    if dir_name != "/":
                        for i in range(len(crawling_robots(dir_name))):
                            pprint(
                                f"  |   |_-> {crawling_robots(dir_name)[i]} => {str(check_endpoint_stat(crawling_robots(dir_name)[i]))}"
                            )
                _tmp.append(dir_name)

if args.output:
    open(args.output, "w").write(log)