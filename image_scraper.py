import json
import os
import requests
import time
import urlparse

REDDIT_SFWPORN_URL = 'http://www.reddit.com/r/earthporn+villageporn+cityporn+spaceporn+waterporn+abandonedporn+animalporn+humanporn+botanicalporn+adrenalineporn+destructionporn+machineporn+newsporn+geekporn+bookporn+mapporn+designporn+roomporn+militaryporn+historyporn+quotesporn+skyporn+fireporn+infrastructureporn/.json?limit=100'


def reddit_sfwporn_urls():
    imgur = []
    r = requests.get(REDDIT_SFWPORN_URL)
    j = json.loads(r.content)
    for d in j['data']['children']:
        data = d['data']
        if 'imgur' in data['url']:
            imgur.append(data['url'])
    # Cleanse the URLs.
    for k, v in enumerate(imgur):
        u = list(urlparse.urlparse(v))
        # Index 1 is the netloc.
        if not u[1].startswith('i.'):
            u[1] = 'i.' + u[1]
        # Index 2 is the path.
        if not u[2].endswith(('.jpg', '.png')):
            u[2] = u[2] + '.jpg'  # Just try appending .jpg to the URL.
        # Remove query components and fragments.
        u[3] = ''
        u[4] = ''
        imgur[k] = urlparse.urlunsplit(u[0:5])
    return imgur


def scrape_images(urls=None):
    if not urls:
        urls = reddit_sfwporn_urls()
    for url in urls:
        filename = url.split('/')[-1]
        if not os.path.exists(filename):
            print('Downloading {0}'.format(filename))
            r = requests.get(url)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            # Be a good citizen and wait 10s between downloads.
            time.sleep(10)
        else:
            print('Skipping {0}'.format(filename))
