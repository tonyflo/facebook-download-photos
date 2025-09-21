# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium",
#     "webdriver-manager",
# ]
# ///
# Download Facebook photos that you are tagged in and that you uploaded

import os
import re
import time
import argparse
import selenium
import urllib.request

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (NoSuchElementException, ElementClickInterceptedException,
                                        TimeoutException)
from webdriver_manager.chrome import ChromeDriverManager


def get_element(browser, how, what):
    """Return element or None without raising."""
    try:
        return browser.find_element(how, what)
    except NoSuchElementException:
        return None


def first_present(browser, locator_options, timeout=0):
    """Return the first located element from a list of locator tuples.

    locator_options: list[tuple[By, str]]
    timeout: seconds to wait (0 for immediate)
    """
    if timeout > 0:
        end = time.time() + timeout
        while time.time() < end:
            for how, what in locator_options:
                el = get_element(browser, how, what)
                if el is not None:
                    return el
            time.sleep(0.2)
        return None
    else:
        for how, what in locator_options:
            el = get_element(browser, how, what)
            if el is not None:
                return el
        return None


def safe_click(browser, element):
    """Attempt normal click, fallback to JS click if intercepted."""
    if element is None:
        return False
    try:
        element.click()
        return True
    except ElementClickInterceptedException:
        # attempt scrolling and JS click
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            browser.execute_script("arguments[0].click();", element)
            return True
    except Exception:
        return False


def dismiss_cookie_dialog(browser):
    """Best-effort cookie dialog dismissal before login.

    Facebook deploys many variants; we try several common button texts / data-testids.
    This should be safe even if elements not present.
    """
    candidates = [
        (By.XPATH, "//button[contains(., 'Allow all cookies')]") ,
        (By.XPATH, "//button[contains(., 'Only allow essential cookies')]") ,
        (By.XPATH, "//button[contains(., 'Decline optional cookies')]") ,
        (By.XPATH, "//div[@role='dialog']//button[contains(., 'Decline')]"),
        (By.XPATH, "//div[@role='dialog']//button[contains(., 'Allow all')]"),
    ]
    for how, what in candidates:
        el = get_element(browser, how, what)
        if el:
            if safe_click(browser, el):
                return True
    return False

# hit right arrow key to go to next photo
# return fbid of photo
def next_photo(browser, timeout=1):
    body = get_element(browser, By.XPATH, '/html/body')
    if body is None:
        return  None

    body.send_keys(Keys.RIGHT)
    time.sleep(timeout) # wait this many seconds

    return get_photo_id(browser.current_url)

# open the first photo in album that's displayed on the page
# returns the url of the first photo in the album
def open_album(browser):
    """Open first photo currently visible in album grid.

    Facebook markup changes often; we attempt a few strategies:
    1. look for anchor with href containing 'photo.php'
    2. look for anchor with href starting with /photo
    Return the navigated photo URL or None.
    """
    photo_selectors = [
        (By.CSS_SELECTOR, "a[href*='photo.php']"),
        (By.XPATH, "//a[contains(@href,'photo.php')]") ,
        (By.XPATH, "//a[starts-with(@href,'/photo')]") ,
    ]
    link = first_present(browser, photo_selectors, timeout=5)
    if not link:
        return None
    href = link.get_attribute('href')
    if not href:
        return None
    browser.get(href)
    return browser.current_url

# extract the fbid for the photo at the url
def get_photo_id(url):
    try:
        pid = re.search(r'fbid=(?P<pid>\d+)\&', url).group('pid')
    except AttributeError:
        pid = ''
    return pid

def logged_in(browser):
    return 'login' not in browser.current_url

def is_two_step(browser):
    return 'two_step_verification' in browser.current_url

def checkpoint_passed(driver):
    return 'checkpoint' not in driver.current_url

def go():
    args = get_args()
    album = args.album
    username = args.username
    timeout = args.timeout

    print('Opening Google Chrome browser')
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    options = Options()
    options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print('Going to Facebook')
    fb_url = 'https://www.facebook.com/login'
    browser.get(fb_url)
    # pre-login cookie dialog dismissal
    dismiss_cookie_dialog(browser)
    if not logged_in(browser):
        print('Logging into Facebook')
        # Wait for inputs
        try:
            WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, "email")))
        except TimeoutException:
            print('ERROR: Email field not found; page structure may have changed.')
            return
        email = first_present(browser, [(By.ID, "email"), (By.NAME, "email")])
        password = first_present(browser, [(By.ID, "pass"), (By.NAME, "pass")])
        if not email or not password:
            print('ERROR: Unable to find login form elements.')
            return
        email.clear(); password.clear()
        email.send_keys(args.email)
        password.send_keys(args.password)
        # Try clicking login button; fallback to ENTER
        login_button = first_present(browser, [
            (By.ID, 'loginbutton'),
            (By.NAME, 'login'),
            (By.XPATH, "//button[@type='submit' and @name='login']"),
        ])
        if login_button:
            # Wait until clickable
            try:
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='loginbutton' or @name='login']")))
            except TimeoutException:
                pass
            clicked = safe_click(browser, login_button)
            if not clicked:
                password.send_keys(Keys.ENTER)
        else:
            password.send_keys(Keys.ENTER)
        # Wait for navigation / success or potential 2FA
        time.sleep(3)
        if is_two_step(browser):
            input('🚨 Two-step or captcha detected. Complete it in the browser then press ENTER here to continue. 🚨')
            time.sleep(3)
        browser.get(browser.current_url)

    if not logged_in(browser):
        print('Login failed. Please check your credentials')
        return
    
    # Try again after login for any lingering cookie dialogs
    dismiss_cookie_dialog(browser)

    print('Going to profile page for ' + username)
    fb_profile = 'https://www.facebook.com/{}'.format(username)
    browser.get(fb_profile)

    print('Going to photos page for ' + username)
    fb_photos = 'https://www.facebook.com/{}/photos'.format(username)
    if 'profile.php' in browser.current_url:
        # FB profiles without username have different URL
        fb_photos = browser.current_url + '&sk=photos'
    browser.get(fb_photos)

    print('Opening "{}" photo album'.format(album))
    fb_photo_album = fb_photos + '_' + album
    browser.get(fb_photo_album)

    print('Loading first photo')
    try:
        first_photo = open_album(browser)
    except AttributeError:
        print('User does not have "{}" album'.format(album))
        return
    if first_photo is None:
        print('User does not have "{}" album'.format(album))
        return

    first_photo_id = get_photo_id(first_photo)

    # loop over all photos in Facebook album
    print('Downloading all {} "{}" photos...'.format(username, album))
    count_download = 0
    count_total = 0
    number_of_photos = 'an unknown'
    while True:
        current_photo = browser.current_url
        if 'videos' in current_photo:
            print('Skipping video: {}'.format(current_photo))
            next_photo(browser, timeout)
            continue

        count_total = count_total + 1
        try:
            success = download(browser, username, album)
        except RuntimeError as e:
            print('ERROR: Facebook blocked this account for "going too fast".')
            print('  This is tempoary, but you must wait before trying again.')
            print('  Pick a longer wait time between photos with --timeout.')
            break

        if not success:
            continue

        count_download = count_download + 1

        photo_id = next_photo(browser, timeout)
        if (photo_id == first_photo_id):
            number_of_photos = str(count_total)
            break

        if photo_id is None:
            print('ERROR: No HTML body at {}'.format(current_photo))
            continue

    print('Downloaded {}/{} photos (of {} total)'.format(
        count_download, 
        count_total,
        number_of_photos))

# download photo
def download(browser, username, album):
    # update browser object with content from current url
    browser.get(browser.current_url)

    # find the relevant tag containing link to photo
    xpath_str = '''//script[contains( text( ), 'image":{"uri')]'''
    script_tag = get_element(browser, By.XPATH, xpath_str)
    if script_tag is None:
        if 'Temporarily Blocked' in browser.page_source:
            raise RuntimeError('Temporarily Blocked by FaceBook')
        print('ERROR: No image at {}'.format(browser.current_url))
        return False

    script_html = script_tag.get_attribute('innerHTML')

    # parse the tag for the image url
    html_search = re.search(r'"image":{"uri":"(?P<uri>.*?)"', script_html)
    uri = html_search.group('uri').replace('\\', '')

    # determine file type and photo id
    matches = re.search(r'(?P<photo_id>\w+)\.(?P<ext>\w+)\?', uri)
    ext = matches.group('ext')
    photo_id = matches.group('photo_id')

    # parse the tag for the image date
    time_search = re.search(r'"created_time":(?P<timestamp>\d+)', script_html)
    ts = int(time_search.group('timestamp'))
    dt = datetime.utcfromtimestamp(ts).strftime('%Y%m%d')

    # create a filename for the image
    filename_format = "photos/{date}_fb_{album}_{user}_{photo_id}.{ext}"
    filename = filename_format.format(
        date=dt, 
        album=album, 
        user=username, 
        photo_id=photo_id,
        ext=ext,
    )

    # check if already downloaded
    if os.path.isfile(filename):
        print("Photo {} already downloaded".format(filename))
        return True

    # download the image
    print('Downloading {}'.format(uri))
    os.makedirs('photos', exist_ok=True)
    try:
        urllib.request.urlretrieve(uri, filename)
    except urllib.error.URLError as e:
        print('ERROR: Network error: {}'.format(e))
        return False

    # set access and modified times
    os.utime(filename, (ts, ts))

    return True


def get_args():
    print('+-------------------------+')
    print('|Facebook Photo Downloader|')
    print('|By: Tony Teaches Tech    |')
    print('|Date: 2023-03-15         |')
    print('+-------------------------+\n')

    parser = argparse.ArgumentParser(description='Download photos from Facebook')
    parser.add_argument('-e', '--email',
                        type=str,
                        required=True,
                        help='Your Facebook email')
    parser.add_argument('-p', '--password',
                        type=str,
                        required=True,
                        help='Your Facebook password')
    album_help=('Photo album to download (default: %(default)s). '
               'Use "of" to download tagged photos. '
               'Use "by" to download uploaded photos.')
    parser.add_argument('-a', '--album',
                        type=str,
                        required=False,
                        choices=['of', 'by'],
                        default='of',
                        help=album_help)
    parser.add_argument('-u', '--username',
                        type=str,
                        required=False,
                        default='me',
                        help='Facebook username to download photos from')
    timeout_help=('Wait this many seconds between photos '
                  '(default: %(default)s)')
    parser.add_argument('-t', '--timeout',
                        type=int,
                        required=False,
                        default=2,
                        help=timeout_help)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    go()


