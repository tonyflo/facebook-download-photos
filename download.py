import re
import time
import urllib.request
from browser import open_chrome
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# hit right arrow key to go to next photo
# return fbid of photo
def next_photo(browser):
    body = browser.find_element_by_xpath('/html/body')
    body.send_keys(Keys.RIGHT)

    time.sleep(1) # wait this many seconds

    return get_photo_id(browser.current_url)

# open the first photo in album that's displayed on the page
# returns the url of the first photo in the album
def open_album(browser):
    photo_str = 'photo.php'
    photo_base = 'https://www.facebook.com/photo'
    photos_tag = browser.find_element_by_xpath ('''//div[contains( text( ), photo_str)]''')
    photos_html = photos_tag.get_attribute('innerHTML')
    photo_id = re.search('(href="'+ photo_base + '\.php(?P<pid>.*?)")', photos_html).group('pid')
    photo_url = photo_base + photo_id
    photo_url = photo_url.replace('amp;','') # remove these from url
    browser.get(photo_url)

    return photo_url

def get_photo_id(url):
    try:
        pid = re.search('fbid=(?P<pid>\d+)\&', url).group('pid')
    except AttributeError:
        pid = ''
    return pid

def go():
    username = 'raddfood'

    # open Google Chrome
    browser = open_chrome()

    # go to Facebook user's photos
    fb_photos = 'https://www.facebook.com/{}/photos'.format(username)
    browser.get(fb_photos)
    first_photo = open_album(browser)
    first_photo_id =  get_photo_id(first_photo)

    # loop over all photos in Facebook album
    # first photo will be downloaded last
    count = 0
    while True:
        current_photo = browser.current_url
        if 'videos' in current_photo:
            print('Skipping video: {}'.format(current_photo))
            next_photo(browser)
            continue

        sequence = str(count).zfill(6)
        download(browser, sequence)

        next_photo_id = next_photo(browser)
        if (next_photo_id == first_photo_id):
            break
        count = count + 1

    print('Downloaded {} Facebook photos'.format(count))

def download(browser, sequence):
    # update browser object with content from current url
    browser.get(browser.current_url)

    # find the relevant tag containing link to photo
    script_tag = browser.find_element_by_xpath ('''//script[contains( text( ), 'image":{"uri')]''')

    # parse the tag for the image url
    script_html = script_tag.get_attribute('innerHTML')
    uri = re.search('"image":{"uri":"(?P<uri>.*?)"', script_html).group('uri').replace('\\', '')
    print('Downloading {}'.format(uri))

    # determine file type
    ext = re.search('\.(?P<ext>\w+)\?', uri).group('ext')

    # parse the tag for the image date
    ts = re.search('"created_time":(?P<timestamp>\d+)', script_html).group('timestamp')
    ts = int(ts)
    dt = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')

    # create a filename for the image
    filename = "photos/facebook_{}_{}.{}".format(dt, sequence, ext)

    # download the image
    urllib.request.urlretrieve(uri, filename)

go()

