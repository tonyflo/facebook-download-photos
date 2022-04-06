# Download Facebook photos that you are tagged in and that you uploaded

import os
import re
import time
import argparse
import urllib.request

from datetime import datetime
from selenium import webdriver
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
    xpath_str = '''//div[contains( text( ), photo_str)]'''
    photos_tag = browser.find_element_by_xpath(xpath_str)
    photos_html = photos_tag.get_attribute('innerHTML')
    photo_search_str = '(href="'+ photo_base + '\.php(?P<pid>.*?)")'
    photo_search = re.search(photo_search_str, photos_html)
    photo_id = photo_search.group('pid')
    photo_url = photo_base + photo_id
    photo_url = photo_url.replace('amp;','') # remove these from url
    browser.get(photo_url)

    return photo_url

# extract the fbid for the photo at the url
def get_photo_id(url):
    try:
        pid = re.search('fbid=(?P<pid>\d+)\&', url).group('pid')
    except AttributeError:
        pid = ''
    return pid

def go():
    args = get_args()
    album = args.album
    username = args.username

    print('Opening Google Chrome browser')
    options = Options()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    browser = webdriver.Chrome(executable_path='./chromedriver',
                               chrome_options=options)

    print('Going to Facebook')
    fb_url = 'https://www.facebook.com/login'
    browser.get(fb_url)
    if ('Log into' in browser.title or
       'Log In' in browser.title or
       'Page Not Found' in browser.title):
        print('Logging into Facebook')
        email = browser.find_element_by_id("email")
        password = browser.find_element_by_id("pass")
        submit = browser.find_element_by_id("loginbutton")
        email.send_keys(args.email)
        password.send_keys(args.password)
        submit.click()
        time.sleep(3) # wait this many seconds

    print('Going to photos page')
    fb_photos = 'https://www.facebook.com/{}/photos'.format(username)
    browser.get(fb_photos)

    # check if login was successful
    if username not in browser.current_url:
        print('Login failed. Please check your credentials')
        return

    print('Opening photo album')
    fb_photo_album = fb_photos + '_' + album
    browser.get(fb_photo_album)

    print('Loading first photo')
    first_photo = open_album(browser)
    first_photo_id = get_photo_id(first_photo)

    # loop over all photos in Facebook album
    print('Downloading all photos...')
    count = 1
    while True:
        current_photo = browser.current_url
        if 'videos' in current_photo:
            print('Skipping video: {}'.format(current_photo))
            next_photo(browser)
            continue

        sequence = str(count).zfill(6)
        download(browser, album, sequence)

        next_photo_id = next_photo(browser)
        if (next_photo_id == first_photo_id):
            break
        count = count + 1

    print('Downloaded {} Facebook photos'.format(count))

# download photo
def download(browser, album, sequence):
    # update browser object with content from current url
    browser.get(browser.current_url)

    # find the relevant tag containing link to photo
    xpath_str = '''//script[contains( text( ), 'image":{"uri')]'''
    script_tag = browser.find_element_by_xpath(xpath_str)
    script_html = script_tag.get_attribute('innerHTML')

    # parse the tag for the image url
    html_search = re.search('"image":{"uri":"(?P<uri>.*?)"', script_html)
    uri = html_search.group('uri').replace('\\', '')
    print('Downloading {}'.format(uri))

    # determine file type
    ext = re.search('\.(?P<ext>\w+)\?', uri).group('ext')

    # parse the tag for the image date
    time_search = re.search('"created_time":(?P<timestamp>\d+)', script_html)
    ts = int(time_search.group('timestamp'))
    dt = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')

    # create a filename for the image
    filename = "photos/fb_{}_{}_{}.{}".format(dt, album, sequence, ext)

    # download the image
    urllib.request.urlretrieve(uri, filename)

    # set access and modified times
    os.utime(filename, (ts, ts))


def get_args():
    print('+-------------------------+')
    print('|Facebook Photo Downloader|')
    print('|By: Tony Teaches Tech    |')
    print('|Date: 2022-04-06         |')
    print('+-------------------------+\n')

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username',
                        type=str,
                        required=True,
                        help='Facebook username')
    parser.add_argument('-e', '--email',
                        type=str,
                        required=True,
                        help='Facebook email')
    parser.add_argument('-p', '--password',
                        type=str,
                        required=True,
                        help='Facebook password')
    album_help=('Photo album to download (default: %(default)s). '
               'Use "of" to download tagged photos of you. '
               'Use "by" to download your uploaded photos.')
    parser.add_argument('-a', '--album',
                        type=str,
                        required=False,
                        choices=['of', 'by'],
                        default='of',
                        help=album_help)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    go()


