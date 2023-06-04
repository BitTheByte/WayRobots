import requests
import re


def wbm_calendarcaptures(url, years):
    """
        Returns snapshot of a URL by specific years 
    """

    snapshots  = []

    for year in years:
        try:
            result = requests.get(
                f"http://web.archive.org/__wb/calendarcaptures?url={url}&selected_year={year}"
            ).json()
        except:
            return []

        for month in range(0, 12):

            current_day = 0
            m_search    = result[month]
            weeks       = len(m_search)

            for days in range(weeks):
                for day in m_search[days]:
                    if day is None or day == {}: continue
                    current_day += 1
                    status_code = day['st'][0]
                    snapshots.extend(
                        [
                            f"http://web.archive.org/web/{timestamp}if_/{url}",
                            status_code,
                        ]
                        for timestamp in day['ts']
                        if status_code != "-"
                    )
    return snapshots




def wbm_sparkline(url):
    """
        Returns Recorded Years
    """
    return (
        requests.get(
            f"https://web.archive.org/__wb/sparkline?url={url}&collection=web&output=json"
        )
        .json()["years"]
        .keys()
    )




def wbm_locate_robots_file(host):
    """
        Attemps to find robots.txt file stored on different subdomains
    """
    content = requests.get(
        f"http://web.archive.org/cdx/m_search/cdx?url=*.{host}/*&output=txt&fl=original&collapse=urlkey"
    ).content
    return re.findall(r".*?.%s.*/robots\.txt" % host, content)   