from colorama import Fore,init
import argparse
import requests
import time
import re

init(autoreset=True)
log =""

def pprint(out):
	global log
	log += out+"\n"

	out = " " + out
	if "[ERROR]" in out:
		out = out.replace("[ERROR]","[%sERROR%s]" % (Fore.RED,Fore.RESET))

	if "[WARNING]" in out:
		out = out.replace("[WARNING]","[%sWARNING]%s" % (Fore.LIGHTWHITE_EX,Fore.YELLOW))

	if "[robots.txt]" in out:
		out = out.replace("[robots.txt]" , "[%srobots.txt%s]" % (Fore.LIGHTBLACK_EX,Fore.RESET))

	if "->" in out:
		out = out.replace("->" , "->%s" % (Fore.LIGHTBLUE_EX))
 
	if "*-" in out:
		out = out.replace("*-" , "%s*%s-%s" % (Fore.BLUE,Fore.RED,Fore.LIGHTWHITE_EX))

	if ":[" in out:
		out = out.replace(":[" , ":[%s" % Fore.LIGHTRED_EX)
		out = out.replace("]","%s]" % Fore.WHITE)
	print(out)

def parse_robots(txt):
	txt = txt.split("\n")
	res = []
	for line in txt:
		if not "#" in line:
			if ":" in line and "/" in line and not "http" in line:
				res.append(  line.split(":")[1].strip()  )
	return res


def fetch_content(ts,target):
	ts_dirs = []
	for timestap in ts:
		content = requests.get("http://web.archive.org/web/{}if_/{}".format(timestap,target)).content
		dirs = parse_robots(content)
		ts_dirs.append({timestap:dirs})
	return ts_dirs
	

def wayback_find_robots(host):
	content = requests.get("http://web.archive.org/cdx/m_search/cdx?url=*.{}/*&output=txt&fl=original&collapse=urlkey".format(host)).content
	robots_files = re.findall(r".*?.%s/robots\.txt" % host,content)	
	return robots_files


def wayback_url(url,year):
	allowed_statuses = [200]
	result = requests.get("http://web.archive.org/__wb/calendarcaptures?url={}&selected_year={}".format(url,year)).json()

	for month in range(0,12):

		m_search = result[month]
		days   = len(m_search)
		current_day = 0

		for days_row in range(days):
			for day_data in m_search[days_row]:

				if day_data != None:
					current_day += 1

					if day_data != {}:
						ts = day_data['ts']
						st = day_data['st'][0]

						if st in allowed_statuses:
							timestamp2dir = fetch_content(ts, url)

							for i in timestamp2dir:
								for ts,val in i.items():
									yield ts,val


parser = argparse.ArgumentParser(description='Welcome to WayRobots help page')
parser.add_argument('-i','--input',type=str, help='Target host')
parser.add_argument('-o','--output',type=str, help='Output file')
parser.add_argument('-y','--year',type=str, help='Years Range e.g[2014-2019]')
args = parser.parse_args()

if not args.input:
	pprint("[ERROR] Please specify the target first using -i")
	exit()

if not args.year:
	pprint("[WARNING] You haven't specify the year, Using current year: %s" % time.strftime("%Y"))
	args.year = "%s-%s" % (time.strftime("%Y"),time.strftime("%Y"))

if not "-" in args.year:
	pprint("[ERROR] Please specify starting and ending year e.g[2014-2019]")
	exit()

year   = args.year
target = args.input

pprint("Searching for robots.txt on *.%s" % target)

robots_txt = set(wayback_find_robots(target))

if len(robots_txt) == 0:
	pprint("[ERROR] Wasn't able to find any [robots.txt] files")
	exit()

pprint("Found [robots.txt] on the following:\n\n  *- " + '\n  *- '.join(robots_txt) + "\n")

year_from = int(year.split("-")[0])
year_to   = int(year.split("-")[1])

for year in range(year_from,year_to +1):
	for robot_file in robots_txt:
		pprint("[%s]::[%s] Searching for [robots.txt] snapshot" %  (year,robot_file) )
		wb = wayback_url(robot_file, year)

		_tmp = []
		for result in wb:
			for dir_name in result[1]:
				if not dir_name in _tmp:
					pprint("  |_-> " + dir_name)
				_tmp.append(dir_name)

if args.output:
	open(args.output,"w").write(log)
