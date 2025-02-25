# Download Facebook Photos
This script will download all of your Facebook photos.

I wanted to delete my Facebook profile since I rarely use it anymore. While Facebook allows you to [download a copy of your data](https://www.facebook.com/help/212802592074644), this does not include photos that you are tagged in. Additionally, some of these photos are not high resolution.

So I decided to write this script to download Facebook photos that you're tagged in and that you have uploaded. This script can also download photos of other Facebook users that have public pictures.

## How to Download All Your Photos from Facebook

**NOTE:** You will need to have [Python 3 & uv](https://docs.astral.sh/uv/getting-started/installation/), Google Chrome, and optionally git installed.

This code was tested on macOS and Linux, but should also work on Windows.
 
### 1. Clone or download this repository
```sh
git clone https://github.com/tonyflo/facebook-download-photos.git
cd facebook-download-photos
```

### 2. Download Facebook photos you're tagged in
Execute the following command to download all Facebook photos that you are tagged in.
```sh
uv run download.py -e you@example.com -p password -a of
```
**NOTE:** *Be sure to replace *email* and *password* with your actual Facebook username, email, and password.*

### 3. Download Facebook photos you've uploaded
```sh
uv run download.py -e you@example.com -p password -a by
```
**NOTE:** *Be sure to replace *email* and *password* with your actual Facebook username, email, and password.*

### 4. Download someone else's Facebook photos
```
uv run download.py -u username -e you@example.com -p password -a of
uv run download.py -u username -e you@example.com -p password -a by
```

### Running without uv

If you don't want to install uv, you can run the script with a python env as well. For example:

```sh
python3 -m venv ~/env/fb
source ~/env/fb/bin/activate

python3 -m pip install --upgrade pip
pip install selenium
pip install webdriver-manager

python download.py -e you@example.com -p password -a by
```

## Command Overview
```
usage: download.py [-h] -e EMAIL -p PASSWORD [-a {of,by}] [-u USERNAME]

Download photos from Facebook

optional arguments:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        Your Facebook email
  -p PASSWORD, --password PASSWORD
                        Your Facebook password
  -a {of,by}, --album {of,by}
                        Photo album to download (default: of). Use "of" to download
                        tagged photos. Use "by" to download uploaded photos.
  -u USERNAME, --username USERNAME
                        Facebook username to download photos from
  -t TIMEOUT, --timeout TIMEOUT
                        Wait this many seconds between photos (default: 2)
```
