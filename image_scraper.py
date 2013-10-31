#!/usr/bin/python
from __future__ import print_function
import flickrapi
import json
import os
import time
import urlparse
import urllib

REDDIT_SFWPORN_URL = 'http://www.reddit.com/r/earthporn+cityporn+spaceporn+waterporn+abandonedporn+animalporn+botanicalporn+destructionporn+machineporn+militaryporn+skyporn+fireporn+infrastructureporn+fogporn/.json?limit=100'


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
    if not posts:  # Occasionally the script returns no JSON.
        return None
    urls = []
    flickr_api_key = open('FLICKR_API_KEY', 'r').readline().strip()  # Substitute your own API key.
    flickr = flickrapi.FlickrAPI(flickr_api_key)
    for i in posts:
        urls.append(i['url'])
    # Cleanse the URLs.
    for k, v in enumerate(urls):
        u = list(urlparse.urlparse(v))
        # Index 1 is the netloc.
        if 'imgur' in u[1]:  # Append "i." to the start of imgur URLs.
            if not u[1].startswith('i.'):
                u[1] = 'i.' + u[1]
            # Index 2 is the path.
            if not u[2].endswith(('.jpg', '.jpeg', '.png', '.gif')):
                u[2] = u[2] + '.jpg'  # Just try appending .jpg to the URL.
            # Remove query components and fragments.
            u[3], u[4] = ('', '')
            urls[k] = urlparse.urlunsplit(u[0:5])
        if not 'staticflickr' in u[1] and 'flickr' in u[1]:
            print('Obtaining photo details from Flickr: {0}'.format(u[2]))
            # From the path, get the photo ID.
            photo_id = u[2].split('/')[3]
            photo_sizes = flickr.photos_getSizes(
                api_key=flickr_api_key, photo_id=photo_id, format='json')
            photo_sizes = photo_sizes[14:-1]  # Remove the extra from the return string.
            photo_sizes = json.loads(photo_sizes)  # Turn it into a dict.
            photo_sizes = photo_sizes['sizes']
            height = 0
            url = ''
            for pic in photo_sizes['size']:  # Iterate through all sizes, looking for the largest.
                y = int(pic['height'])
                if y > height:
                    height = y
                    url = pic['source']
            urls[k] = url
    return urls


def scrape_images(log_json=False, save_path=None):
    '''
    Gets posts from Subreddits, then tries to download all the images to the
    local directory.
    Skips any images that exist locally, and pauses 10s between downloads.
    '''
    posts = None
    while posts is None:
        # Sometimes parsing the Reddit feed fails. If so, wait 5 seconds
        # and retry.
        print('Attempting to scrape Reddit posts.')
        posts = reddit_sfwporn_posts()
        time.sleep(3)
    urls = zip(parse_post_urls(posts), posts)
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    for url in urls:
        filename = url[0].split('/')[-1]
        if save_path:  # Path to save images was supplied.
            path = os.path.join(save_path, filename)
        else:  # No path supplied: default to a directory called 'img' in the current dir.
            path = os.path.join(scriptpath, 'img', filename)
        if not os.path.exists(path):
            print('Downloading {0}...'.format(filename), end='')
            try:
                urllib.urlretrieve(url[0], path)
                print('done (pausing 10s).')
                # Be a good net citizen and wait 10s between downloads.
                time.sleep(10)
                if log_json:
                    print('Writing to log for {0}'.format(url[0]))
                    # Create json log file, if required.
                    if not os.path.exists(os.path.join(scriptpath, 'reddit_posts.json')):
                        f = open(os.path.join(scriptpath, 'reddit_posts.json'), 'w+')
                        f.close()
                    # Append the post JSON to a file, for record-keeping.
                    f = open(os.path.join(scriptpath, 'reddit_posts.json'), 'r')
                    try:
                        j = json.loads(f.read())  # Should be a list of dicts.
                    except:
                        j = []
                    f.close()
                    j.append({
                        'permalink': url[1]['permalink'],
                        'title': url[1]['title'],
                        'url': url[0]
                    })
                    f = open(os.path.join(scriptpath, 'reddit_posts.json'), 'w')
                    f.write(json.dumps(j))
                    f.close()
            except:
                print('error! Skipping it.')
                try:  # Write failed URLS to a file for debugging.
                    f = open(os.path.join(scriptpath, 'failed_downloads.txt'), 'a')
                    f.write(url[0] + '\n')
                    f.close()
                except:
                    pass
        else:
            print('Skipping {0} (it already exists).'.format(filename))


if __name__ == '__main__':
    scrape_images(log_json=True)
