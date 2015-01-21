__author__ = 'Sushant'
import time
import os

from BeautifulSoup import BeautifulSoup

from Web import Web
from UnicodeCSV import UnicodeReader, UnicodeWriter


class OpenDNSScraper(object):
    def __init__(self, domains_list_csv, output_csv_prefix, start_domain_id, end_domain_id):
        with open(domains_list_csv, "rb") as domains_list:
            output = []
            first = None
            last = None

            W = Web()
            reader = UnicodeReader(domains_list, delimiter=",")
            for row in reader:
                domain_id = int(row[0])
                domain_name = row[1]

                if domain_id < start_domain_id:
                    continue

                if first is None:
                    first = domain_id

                code, content = W.get_url_contents("https://domain.opendns.com/" + domain_name)

                if code == 200:
                    domain = ""
                    isAdult = None
                    isTopSite = False
                    confirmed_tags = []
                    soup = BeautifulSoup(content)
                    maindiv = soup.find(id="maincontent")
                    if maindiv:
                        main_col = maindiv.findAll("div", {"class": "col x4"})
                        if main_col:
                            # print main_col[0].contents[1]
                            h2 = main_col[0].findAll("h2")
                            if h2:
                                domain = h2[0].getText()
                                site_icon = h2[0].findAll("img", {
                                "src": "https://d2v7u03x06aro3.cloudfront.net/img/icon_topsite.gif"})
                                if site_icon:
                                    isTopSite = True
                                    domain = domain.split()[0]
                            screenshot_div = main_col[0].findAll("div", {"class": "screenshot"})
                            if screenshot_div:
                                screenshot_link = screenshot_div[0].findAll("a", {"class": "adult"})
                                if screenshot_link:
                                    isAdult = True
                                else:
                                    screenshot_link = screenshot_div[0].findAll("a", {"class": "normal"})
                                    if screenshot_link:
                                        isAdult = False

                        tags_div = maindiv.findAll("div", {"class": "col x3 end"})
                        if tags_div:
                            h3 = tags_div[0].findAll("h3")
                            if h3:
                                txt = h3[0].getText()
                                if txt.startswith("Tagged:"):
                                    tag_string = txt[7:]
                                    # print tag_string
                                    splits = tag_string.split(",")
                                    for tag in splits:
                                        confirmed_tags.append(tag.strip())
                    adult_flag = "Unknown"
                    if isAdult is not None:
                        if isAdult == True:
                            adult_flag = "1"
                        else:
                            adult_flag = "0"

                    top_site_flag = "0"
                    if isTopSite == True:
                        top_site_flag = "1"

                    confirmed_tags_compilation = "|".join(confirmed_tags)

                    output.append([repr(domain_id), domain, adult_flag, top_site_flag, confirmed_tags_compilation])

                    if domain_id >= end_domain_id:
                        if last is None:
                            last = domain_id
                        output_csv = output_csv_prefix + "_" + repr(first) + "_" + repr(last) + ".csv"
                        with open(output_csv, "wb") as output_csv:
                            writer = UnicodeWriter(output_csv, delimiter=",")
                            for out_row in output:
                                writer.writerow(out_row)
                        return


current_milli_time = lambda: int(round(time.time() * 1000))

cwd = os.path.curdir

input_csv = os.path.join(cwd, "..", "data", "raw", "domains.csv")
output_csv_prefix = os.path.join(cwd, "..", "data", "raw", "gathered")

time_start = current_milli_time()
O = OpenDNSScraper(input_csv, output_csv_prefix, 80000, 80100)
time_end = current_milli_time()

print "Time taken : " + str(time_end - time_start) + " milliseconds!"