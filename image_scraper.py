#!/usr/local/bin/python
from __future__ import print_function
import json
import os
import time
import urlparse
import urllib

REDDIT_SFWPORN_URL = 'http://www.reddit.com/r/earthporn+villageporn+cityporn+spaceporn+waterporn+abandonedporn+animalporn+botanicalporn+destructionporn+machineporn+geekporn+bookporn+designporn+militaryporn+historyporn+skyporn+fireporn+infrastructureporn+fogporn/.json?limit=100'


def reddit_sfwporn_posts(ups=100):
    '''
    Returns a list of Reddit posts to image files posted to the FWPorn network,
    with at least ``ups`` number of upvotes.
    '''
    posts = []
    r = urllib.urlopen(REDDIT_SFWPORN_URL)
    j = json.loads(r.read())
    if not 'data' in j:
        return None
    for d in j['data']['children']:
        data = d['data']
        if data['ups'] >= ups:
            posts.append(data)
    return posts


def parse_post_urls(posts):
    '''
    Receives a list of dicts, being the JSON for Reddit posts.
    Pulls the URL out of each and attempts to clean them a bit.
    Won't guarantee that all URLs are valid, but most should be.
    '''
    imgur = []  # Originally I just grabbed Imgur pics.
    for i in posts:
        imgur.append(i['url'])
    # Cleanse the URLs.
    for k, v in enumerate(imgur):
        u = list(urlparse.urlparse(v))
        # Index 1 is the netloc.
        if 'imgur' in u[1]:  # Append "i." to the start of imgur URLs.
            if not u[1].startswith('i.'):
                u[1] = 'i.' + u[1]
        # Index 2 is the path.
        if not u[2].endswith(('.jpg', '.png', '.gif')):
            u[2] = u[2] + '.jpg'  # Just try appending .jpg to the URL.
        # Remove query components and fragments.
        u[3], u[4] = ('', '')
        imgur[k] = urlparse.urlunsplit(u[0:5])
    return imgur


def scrape_images(log_json=False):
    '''
    Gets posts from Reddits, then tries to download all the images to the
    local directory.
    Skips any images that exist locally, and pauses 10s between downloads.
    '''
    posts = reddit_sfwporn_posts()
    urls = parse_post_urls(posts)
    for url in urls:
        filename = url.split('/')[-1]
        if not os.path.exists(filename):
            print('Downloading {0}...'.format(filename), end='')
            try:
                urllib.urlretrieve(url, filename)
                print('done (pausing 10s).')
                # Be a good net citizen and wait 10s between downloads.
                time.sleep(10)
            except:
                print('error! Skipping it.')
                try:  # Write failed URLS to a file for debugging.
                    f = open('failed_downloads.txt', 'a')
                    f.write(url + '\n')
                    f.close()
                except:
                    pass
        else:
            print('Skipping {0}'.format(filename))
    if log_json:
        # Append the posts JSON to a file, for record-keeping.
        f = open('reddit_posts.json', 'w+')
        try:
            j = json.loads(f.read())
        except:
            j = []
        f.close()
        j += posts
        f = open('reddit_posts.json', 'w+')
        f.write(json.dumps(j))
        f.close()


if __name__=='__main__':
    scrape_images(log_json=True)
