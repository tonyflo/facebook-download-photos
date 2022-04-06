import re
import urllib.request
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# open Google Chrome with an existing profile
options = webdriver.ChromeOptions()
options.add_argument('user-data-dir=/Users/tonyflorida/Library/Application Support/Google/Chrome/')
options.add_argument('profile-directory=Profile 15')
browser = webdriver.Chrome(executable_path='/Users/tonyflorida/proxycrawl/chromedriver', chrome_options=options)

# load first photo in Facebook photo album
browser.get('https://www.facebook.com/photo.php?fbid=10158024296404560&set=t.633032338&type=3')

# find the relevant tag containing link to photo
script_tag = browser.find_element_by_xpath ('''//script[contains( text( ), 'image":{"uri')]''')

# parse the tag for the image url
script_html = script_tag.get_attribute('innerHTML')
uri = re.search('"image":{"uri":"(?P<uri>.*?)"', script_html).group('uri').replace('\\', '')

# parse the tag for the image date
ts = re.search('"created_time":(?P<timestamp>\d+)', script_html).group('timestamp')
ts = int(ts)
dt = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')

# create a filename for the image
filename = "facebook_{}.jpg".format(dt)

# download the image
urllib.request.urlretrieve(uri, filename)


#body = browser.find_element_by_xpath('/html/body')
#body.send_keys(Keys.RIGHT)

#elem = browser.find_element(By.NAME, 'p')  # Find the search box
#elem.send_keys('seleniumhq' + Keys.RETURN)


