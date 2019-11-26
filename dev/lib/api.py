import requests
import re


def wbm_calendarcaptures(url, years):
    """
        Returns snapshot of a URL by specific years 
    """

    snapshots  = []

    for year in years:
        try:
            result = requests.get("http://web.archive.org/__wb/calendarcaptures?url={}&selected_year={}".format(url, year)).json()
        except:
            return []

        for month in range(0, 12):

            current_day = 0
            m_search    = result[month]
            weeks       = len(m_search)
            
            for days in range(weeks):
                for day in m_search[days]:
                    if day == None or day == {}: continue
                    current_day += 1
                    status_code = day['st'][0]
                    for timestamp in day['ts']:
                        if status_code == "-": continue
                        snapshots.append( ["http://web.archive.org/web/{}if_/{}".format(timestamp,url) , status_code] )
    return snapshots




def wbm_sparkline(url):
    """
        Returns Recorded Years
    """
    return requests.get("https://web.archive.org/__wb/sparkline?url={}&collection=web&output=json".format(url)).json()["years"].keys()




def wbm_locate_robots_file(host):
    """
        Attemps to find robots.txt file stored on different subdomains
    """
    content = requests.get("http://web.archive.org/cdx/m_search/cdx?url=*.{}/*&output=txt&fl=original&collapse=urlkey".format(host)).content
    robots_files = re.findall(r".*?.%s.*/robots\.txt" % host, content)
    return robots_files   