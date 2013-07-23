from bottle import route, static_file, run, jinja2_template
import os
from image_scraper import scrape_images
from random import shuffle
from threading import Timer

# Schedule a task to scrape new images.
interval = 6 * 60 * 60  # 6 hour interval.
Timer(interval, scrape_images, kwargs={'log_json': True})

IMGPATH = os.path.join(os.path.dirname(__file__), 'img')


@route('/')
def carousel():
    img_list = os.listdir(IMGPATH)
    img_list = ['img/' + img for img in img_list]
    shuffle(img_list)  # Randomise the order of images.
    img_list = img_list[0:319]  # Slice off the first 320 images.
    return jinja2_template("slideshow.html", img_list=img_list)


@route('/img/<filename>')
def server_static(filename):
    return static_file(filename, root=IMGPATH)

run(host='localhost', port=8181, debug=True, reloader=True)
