from selenium import webdriver


# open Google Chrome with an existing profile
def open_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=/Users/tonyflorida/Library/Application Support/Google/Chrome/')
    options.add_argument('profile-directory=Profile 15')
    browser = webdriver.Chrome(executable_path='./chromedriver', chrome_options=options)

    return browser

if __name__ == '__main__':
    browser = open_chrome()

