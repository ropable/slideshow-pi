#!/usr/bin/python
from __future__ import print_function
import os
import requests
import urllib
import time
from xml.dom import minidom


URL = 'https://storage.googleapis.com/chromeos-wallpaper-public/'


def scrape_images():
    c = requests.get(URL)
    if not c.status_code == 200:
        return 'Error: URL returns status {0}'.format(c.status_code)
    xmldoc = minidom.parseString(c.content)
    keys = xmldoc.getElementsByTagName('Key')
    imgs = []
    for key in keys:
        s = key.childNodes[0].data
        if s[-3:] in ['jpg', 'png']:
            imgs.append(s)
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    for img in imgs:
        if not 'thumbnail' in img:
            path = os.path.join(scriptpath, 'img', img)
            url = URL + img
            print('Downloading {0}...'.format(img), end='')
            urllib.urlretrieve(url, path)
            print('done (pausing 2s).')
            time.sleep(2)


if __name__ == '__main__':
    scrape_images()
