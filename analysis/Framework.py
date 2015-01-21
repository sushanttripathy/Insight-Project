__author__ = 'Sushant'
from web import Web
from BeautifulSoup import BeautifulSoup
import re
import urlparse
import urllib2
import threading
import os
import uuid

class DownloadFiles(object):
    def __init__(self, files_list, download_folder, num_threads = 8):
        self.lock = threading.Lock()
        self.coordinator = {}
        tgrp = []
        for file in files_list:
            t = threading.Thread(target=self.__download_file, args=[file, download_folder])
            t.start()
            tgrp.append(t)
            if len(tgrp) > num_threads:
                while len(tgrp):
                    tgrp.pop().join()
        while len(tgrp):
            tgrp.pop().join()

    def __download_file(self, file_url, destination):
        try:
            #print "Downloading " + file_url
            dlder = urllib2.urlopen(file_url)
            destination_path  = os.path.join(destination,os.path.basename(file_url))
            self.lock.acquire()
            if destination_path in self.coordinator:
                self.coordinator[destination_path] += 1
                _,extension = os.path.splitext(destination_path)
                unique_name = str(uuid.uuid4())
                destination_path = os.path.join(destination,unique_name+extension)
            else:
                self.coordinator[destination_path] = 1
            self.lock.release()
            #print "Downloading to " + destination_path
            with open(destination_path, "wb") as dld_file:
                dld_file.write(dlder.read())
        except:
            pass


class Framework(Web):
    def get_url(self,url):
        code, content = super(Framework, self).get_url(url)

        ret_content = {}

        if code >= 200 and code <= 400:
            soup = BeautifulSoup(content)
            title = soup.title.string
            #print title

            desc_meta = soup.findAll("meta",attrs={'name':re.compile("^description$", re.I)})
            if not desc_meta or not len(desc_meta):
                desc_meta = soup.findAll("meta",attrs={'http-equiv':re.compile("^description$", re.I)})
            description = None
            if desc_meta is not None and len(desc_meta) and desc_meta[0].has_key('content'):
                #print desc_meta
                description = desc_meta[0]['content']
            #print description

            keyw_meta = soup.findAll("meta",attrs={'name':re.compile("^keywords$", re.I)})

            if not keyw_meta or not len(keyw_meta):
                keyw_meta = soup.findAll("meta",attrs={'http-equiv':re.compile("^keywords$", re.I)})

            keywords = None
            if keyw_meta is not None and len(keyw_meta) and keyw_meta[0].has_key('content'):
                keywords = keyw_meta[0]['content']
            #print keywords

            text = soup.getText()
            #print text

            imgs = soup.findAll("img")
            images = []
            image_alts = []
            for img in imgs:
                if img.has_key('src'):
                    parsed = urlparse.urlparse(img['src'])
                    if parsed.scheme:
                        images.append(img['src'])
                    else:
                        images.append(urlparse.urljoin(url, img['src']))
                if img.has_key('alt'):
                    #print img['alt']
                    image_alts.append(img['alt'])

            #print images
            ret_content['title'] = title
            ret_content['description'] = description
            ret_content['keywords'] = keywords
            ret_content['text'] = text
            ret_content['image_alts'] = image_alts
            ret_content['images'] = images

        return code, ret_content

    def get_images(self, image_url_list, download_folder):
        DownloadFiles(image_url_list, download_folder)

    def get_snapshot(self, url):
        pass




F = Framework()

code, content =  F.get_url("https://www.pornhub.com")
cwd  =os.curdir
images_folder = os.path.join(cwd, "..", "data", "raw", "images")
DownloadFiles(content['images'], images_folder)
