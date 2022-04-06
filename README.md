# Download Facebook Photos
This script will download all of your Facebook photos.

I wanted to delete my Facebook profile since I rarely use it anymore. While Facebook allows you to [download a copy of your data](https://www.facebook.com/help/212802592074644), this does not include photos that you are tagged in. Additionally, some of these photos are not high resolution.

So I decided to write this script to download Facebook photos that you're tagged in and that you have uploaded.

## How to Download All Your Photos from Facebook

**NOTE #1:** You will need to have Python 3 and Google Chrome installed

**NOTE #2:** You will need to know your Facebook username. When logged in, you can find your Facebook username at https://facebook.com/me

### 1. Create a virtual Python environment
```
python3 -m venv ~/env/fb
source ~/env/fb/bin/activate
```

### 2. Install the selenium package
```
pip install selenium
```
 
#### 3. Clone this repository
```
git clone git@github.com:tonyflo/facebook-download-photos.git
cd facebook-download-photos
```

### 4. Get the ChromeDriver
Go to https://sites.google.com/chromium.org/driver/ and download the lastest stable release for your opperating system. Extract the contents of the zip file into the *facebook-download-photos* directory.
 
#### 5. Download Facebook photos you're tagged in
Execute the following command to download all Facebook photos that you are tagged in.
```
python download.py -u username -e you@example.com -p password -a of
```
**NOTE:** *Be sure to replace *username*, *email*, and *password* with your actual Facebook username, email, and password.*

6. Download Facebook photos you've uploaded
```
python download.py -u username -e you@example.com -p password -a by
```
**NOTE:** *Be sure to replace *username*, *email*, and *password* with your actual Facebook username, email, and password.*
