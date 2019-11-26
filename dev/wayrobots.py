from lib import *


def parse_robots(txt):
    txt = txt.split("\n")
    res = []
    for line in txt:
        if not "#" in line:
            if ":" in line and "/" in line and not "http" in line:
                res.append(line.split(":")[1].strip())
    return set(res)


def show(s):
    """
        TODO: Support colors as the old version
    """
    print(s)


def wayback_robots(target,threads=20,vaild_codes=[200] ):

    files = set()
    def get_content(url):
        content = requests.get(url).content
        with lock: [files.add(x) for x in parse_robots(content)]

    sparkline        = wbm_sparkline(target)
    calendarcaptures = [capture for capture in wbm_calendarcaptures(url=target,years=sparkline) if capture[1] in vaild_codes]
    threader         = Threader(pool_size=threads)

    for capture in calendarcaptures:
        url    = capture[0]
        status = capture[1]
        threader.put(get_content, [url])

    threader.finish_all()

    return files


parser = argparse.ArgumentParser(description='Welcome to domainker help page')
parser.add_argument('-i', '--input', type=str, help='Target host')
parser.add_argument('-o', '--output', type=str, help='[NOT SUPPORTED YET] Output file')
args = parser.parse_args()

if not args.input:
    pprint("[ERROR] Please specify the target host first using -i")
    exit()

host = args.input
located_robots = wbm_locate_robots_file(host)

show("Found robots.txt on {} Domain(s) ..".format(len(located_robots)))
for d in located_robots: show(" >> {}".format(d) )

for robot in  located_robots :
    urls = sorted( wayback_robots(robot) )
    show("Found on {} ({}) DIR(s)".format(robot,len(urls)))
    if len(urls) == 0: continue

    for url in urls:
        show(" >> {}".format(url))