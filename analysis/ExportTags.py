# -*- coding: utf-8 -*-
__author__ = 'Sushant'
import json
import csv
from ReadJSONDump import ReadJSONDump
import guess_language
from BeautifulSoup import BeautifulSoup
import hashlib
import os
from UnicodeCSV import UnicodeWriter

class ExportTags(ReadJSONDump):
    def __init__(self, input_file, output_file_tags, output_file_redo):
        self.tags = []
        self.redo = []
        self.load_json(input_file)
        self.save_tags(output_file_tags)
        self.save_redo(output_file_redo)

    def load_json(self, input_file, load_ids_only = False):
        with open (input_file, "rb") as in_file:
            while True:
                ret = self.sequential_read_line(in_file)
                if ret is not None:
                    decode = json.loads(ret)
                    self.get_tags(decode)
                    if len(self.tags) == 5:
                        print self.tags
                else:
                    break

    def get_tags(self, json_object):
        http_code = json_object['http_response_code']
        if http_code >= 200 and http_code <= 400:
            description = ""
            if 'description' in json_object:
                description = json_object['description']
            domain = json_object['base_domain']
            domain_id = json_object['domainid']

            sub_domain = ""
            sub_domain_digest = ""
            if 'sub_domain' in json_object:
                sub_domain = json_object['sub_domain']
                sub_domain_digest = json_object['subdomain_digest']

            title = ""
            if 'title' in json_object:
                title = json_object['title']

            text = ""
            if 'text' in json_object:
                text = json_object['text']

            uri = json_object['uri']


            language = ""
            try:
                m = hashlib.md5()
                m.update(uri)
                uri_digest = m.hexdigest()

                if len(text) > 20:
                    soup = BeautifulSoup(text)
                    language = guess_language.guess_language(soup.contents[0])
                else:
                    text_2 = description + text
                    if len(text_2) <  20:
                        text_2 = title + text_2

                    if len(text_2) > 10:
                        soup = BeautifulSoup(text_2)
                        language = guess_language.guess_language(soup.contents[0])
            except:
                self.redo.append(uri)
                return

            row = [str(domain_id), domain, sub_domain_digest, sub_domain, uri_digest, language ]
            self.tags.append(row)

    def save_tags(self, output_file):
        with open(output_file, "wb") as o_file:
            writer = UnicodeWriter(o_file, delimiter=",")
            header = ['domain_id', 'domain', 'sub_domain_digest', 'sub_domain', 'uri', 'language']
            writer.writerow(header)

            for row in self.tags:
                writer.writerow(row)

    def save_redo(self, output_file):
        with open(output_file, "wb") as o_file:
            writer = UnicodeWriter(o_file, delimiter=",")
            for row in self.redo:
                writer.writerow([row])

cwd = os.path.curdir
json_file = os.path.join(cwd, "..", "data", "raw", "round2.json")
tag_file = os.path.join(cwd, "..", "data", "processed", "round2.tags")
redo_file = os.path.join(cwd, "..", "data", "processed", "round2_redo.txt")
E = ExportTags(json_file, tag_file, redo_file)