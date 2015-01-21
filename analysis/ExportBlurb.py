__author__ = 'Sushant'
import os
import json

from BeautifulSoup import BeautifulSoup
import guess_language

from UnicodeCSV import UnicodeWriter, UnicodeReader
from ReadJSONDump import ReadJSONDump


class ExportBlurb(ReadJSONDump):
    def __init__(self, did_lang_csv, json_dir, output_file_dir, language="en"):
        self.maj_lang_map = {}
        self.dump = []
        self.uris = {}
        self.dom_file_counts = {}
        self.output_dir = output_file_dir
        self.language = language
        self.load_did_lang_map(did_lang_csv)
        self.parse_json_dir(json_dir)


    def load_did_lang_map(self, csv_file):
        with open(csv_file, "rb") as in_file:
            reader = UnicodeReader(in_file, delimiter=",")
            for row in reader:
                did = int(row[0])
                tag = row[1]
                self.maj_lang_map[did] = tag

    def parse_json_dir(self, json_dir):
        for file in os.listdir(json_dir):
            full_path = os.path.join(json_dir, file)
            if os.path.isfile(full_path):
                self.load_json(full_path)

    def load_json(self, input_file, load_ids_only=False):
        with open(input_file, "rb") as in_file:
            while True:
                ret = self.sequential_read_line(in_file)
                if ret is not None:
                    decode = json.loads(ret)
                    self.get_tags(decode)
                    # if len(self.dump) == 5:
                    #    print self.dump
                else:
                    break

    def get_tags(self, json_object):
        http_code = json_object['http_response_code']
        if http_code >= 200 and http_code <= 400:
            domain = json_object['base_domain']
            domain_id = int(json_object['domainid'])

            if domain_id in self.maj_lang_map and self.maj_lang_map[domain_id] == self.language:

                title = ""
                if 'title' in json_object:
                    title = json_object['title']

                description = ""
                if 'description' in json_object:
                    description = json_object['description']

                keywords = None
                if 'keywords' in json_object:
                    keywords = json_object['keywords']

                text = ""
                if 'text' in json_object:
                    text = json_object['text']

                uri = json_object['uri']

                if uri in self.uris:
                    return
                else:
                    self.uris[uri] = True

                blurb = ""

                blurb = blurb + title + " "
                blurb = blurb + description + " "
                if keywords is not None and len(keywords):
                    for k in keywords:
                        blurb = blurb + k + " "
                blurb = blurb + text

                cur_page_language = ""
                try:
                    if len(blurb) > 20:
                        soup = BeautifulSoup(blurb)
                        cur_page_language = guess_language.guess_language(soup.contents[0])
                except:
                    return
                if cur_page_language == self.language:
                    output_dir = os.path.join(self.output_dir, str(domain_id))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir)
                    if domain_id not in self.dom_file_counts:
                        self.dom_file_counts[domain_id] = 0

                    self.dom_file_counts[domain_id] += 1

                    output_file = os.path.join(output_dir, str(self.dom_file_counts[domain_id]) + ".txt")
                    with open(output_file, "wb") as out_file:
                        out_file.write(blurb.encode("utf8"))

                        # row = [str(domain_id), uri, blurb]
                        #self.dump.append(row)


    def save_blurb(self, blurb_file):
        with open(blurb_file, "wb") as out_file:
            writer = UnicodeWriter(out_file, delimiter=",")
            writer.writerows(self.dump)


cwd = os.curdir
maj_lang_tags = os.path.join(cwd, "..", "data", "processed", "maj_lang_tags.csv")
json_dir = os.path.join(cwd, "..", "data", "raw", "json")
output_dir = os.path.join(cwd, "..", "data", "processed", "blurb", "en")

R = ExportBlurb(maj_lang_tags, json_dir, output_dir)
