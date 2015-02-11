__author__ = 'Sushant'
import re
import urlparse
import urllib2
import threading
import os
import uuid

from BeautifulSoup import BeautifulSoup

from Web import Web
from Command import Command


class DownloadFiles(object):
    def __init__(self, files_list, download_folder, num_threads=8):
        self.lock = threading.Lock()
        self.coordinator = {}
        thread_group = []
        for file in files_list:
            t = threading.Thread(target=self.__download_file, args=[file, download_folder])
            t.start()
            thread_group.append(t)
            if len(thread_group) > num_threads:
                while len(thread_group):
                    thread_group.pop().join()
        while len(thread_group):
            thread_group.pop().join()

    def __download_file(self, file_url, destination):
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
            response = opener.open(file_url)
            content = response.read()
            code = response.code
            destination_path = os.path.join(destination, os.path.basename(file_url))
            self.lock.acquire()
            if destination_path in self.coordinator:
                self.coordinator[destination_path] += 1
                _, extension = os.path.splitext(destination_path)
                unique_name = str(uuid.uuid4())
                destination_path = os.path.join(destination, unique_name + extension)
            else:
                self.coordinator[destination_path] = 1
            self.lock.release()
            if 200 <= code <= 400:
                with open(destination_path, "wb") as downloaded_file:
                    downloaded_file.write(content)
        except:
            # not issuing any message as that makes for an irritating frontend experience
            pass


class Framework(Web):
    def get_url_contents(self, url):
        code, content = super(Framework, self).get_url_contents(url)

        ret_content = {}

        if code >= 200 and code <= 400:
            soup = BeautifulSoup(content)
            title = soup.title.string

            desc_meta = soup.findAll("meta", attrs={'name': re.compile("^description$", re.I)})
            if not desc_meta or not len(desc_meta):
                desc_meta = soup.findAll("meta", attrs={'http-equiv': re.compile("^description$", re.I)})
            description = None
            if desc_meta is not None and len(desc_meta) and desc_meta[0].has_key('content'):
                description = desc_meta[0]['content']

            keyw_meta = soup.findAll("meta", attrs={'name': re.compile("^keywords$", re.I)})

            if not keyw_meta or not len(keyw_meta):
                keyw_meta = soup.findAll("meta", attrs={'http-equiv': re.compile("^keywords$", re.I)})

            keywords = None
            if keyw_meta is not None and len(keyw_meta) and keyw_meta[0].has_key('content'):
                keywords = keyw_meta[0]['content']

            text = soup.getText()

            img_tags = soup.findAll("img")
            images = []
            image_alts = []
            for img in img_tags:
                if img.has_key('src'):
                    parsed = urlparse.urlparse(img['src'])
                    if parsed.scheme:
                        images.append(img['src'])
                    else:
                        images.append(urlparse.urljoin(url, img['src']))
                if img.has_key('alt'):
                    image_alts.append(img['alt'])

            # print images
            ret_content['title'] = title
            ret_content['description'] = description
            ret_content['keywords'] = keywords
            ret_content['text'] = text
            ret_content['images_alts'] = image_alts
            ret_content['images_urls'] = images

        return code, ret_content

    def get_images(self, images_url_list, download_folder):
        DownloadFiles(images_url_list, download_folder)

    def get_snapshot(self, url, screenshot_image_path):
        # Using PhantomJS for getting the snapshot
        cmd = Command("phantomjs phantom_load.js " + url + " " + screenshot_image_path)
        cmd.run(120)  #run the screenshotting command with a time-out of 120 seconds

"""
#Usage example:
cwd = os.curdir
images_folder = os.path.join(cwd, "..", "data", "raw", "images")
screenshot_path = os.path.join(cwd, "..", "data", "raw", "images", "snapped.png")

url = "https://www.twitter.com"

F = Framework()

code, content = F.get_url_contents(url)

F.get_images(content['images_urls'], images_folder)
F.get_snapshot(url, screenshot_path)
"""