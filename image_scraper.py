from __future__ import print_function
import json
import os
import time
import urlparse
import urllib

REDDIT_SFWPORN_URL = 'http://www.reddit.com/r/earthporn+villageporn+cityporn+spaceporn+waterporn+abandonedporn+animalporn+botanicalporn+destructionporn+machineporn+geekporn+bookporn+designporn+militaryporn+historyporn+skyporn+fireporn+infrastructureporn/.json?limit=100'


def reddit_sfwporn_urls(ups=200):
    '''
    Returns a list of Imgur URLs to image files posted to the Reddit SFWPorn network,
    with at least ``ups`` number of upvotes.
    Won't guarantee that all URLs are valid, but most should be.
    '''
    imgur = []
    r = urllib.urlopen(REDDIT_SFWPORN_URL)
    j = json.loads(r.read())
    for d in j['data']['children']:
        data = d['data']
        if 'imgur' in data['url'] and data['ups'] >= ups:
            imgur.append(data['url'])
    # Cleanse the URLs.
    for k, v in enumerate(imgur):
        u = list(urlparse.urlparse(v))
        # Index 1 is the netloc.
        if not u[1].startswith('i.'):
            u[1] = 'i.' + u[1]
        # Index 2 is the path.
        if not u[2].endswith(('.jpg', '.png', '.gif')):
            u[2] = u[2] + '.jpg'  # Just try appending .jpg to the URL.
        # Remove query components and fragments.
        u[3], u[4] = ('', '')
        imgur[k] = urlparse.urlunsplit(u[0:5])
    return imgur


def scrape_images(urls=None):
    '''
    Tries to download all the images from a passed-in list of URLs into the local directory.
    Skips any images that exist locally, and pauses 10s between downloads.
    '''
    if not urls:
        urls = reddit_sfwporn_urls()
    for url in urls:
        filename = url.split('/')[-1]
        if not os.path.exists(filename):
            print('Downloading {0}...'.format(filename), end='')
            urllib.urlretrieve(url, filename)
            print('done (pausing 10s)')
            # Be a good citizen and wait 10s between downloads.
            time.sleep(10)
        else:
            print('Skipping {0}'.format(filename))

            
if __name__=='__main__':
    scrape_images()