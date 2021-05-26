# PyValidator [![Licensed under the MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/datCloud/PyValidator/blob/master/LICENSE)
Python website validator. Checks W3C, PageSpeed, SEO, Mobile, etc

## Instructions
### On Windows
* [Download and install Python 3.7.4+ for Windows](https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe)
* Before install it, remember to check 'Add Python 3.x to PATH' box on instalation window
* On your command prompt, run the following commands:
```bash
pip install selenium
pip install requests_html
pip install colorama
```
* For this script, the Selenium runs with the latest version of [Mozilla Firefox](https://www.mozilla.org/pt-BR/firefox/new/) and [Geckodriver](https://github.com/mozilla/geckodriver/releases/latest)
* Create a folder in **C:/Users/[YOUR_USER_GOES_HERE]/AppData/** and name it as **Geckodriver**
* Extract the **geckodriver.exe** from the ZIP file and put it in the Geckodriver folder

![Example Geckodriver directory path](/images/example-01.png)

* Open the command prompt and paste fhe following command
```bash
setx path "%path%;C:\Users\YOUR_USER\AppData\Local\Geckodriver"
```
* This command will set the Geckodriver directory in your environment variables
* Restart your computer
* Test the script

### If you have any issue, please let me know :)
