# PyValidator
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
* For this script, the Selenium runs with [Mozilla Firefox 47.0.1](https://ftp.mozilla.org/pub/firefox/releases/47.0.1/win64/pt-BR/Firefox%20Setup%2047.0.1.exe) and [Geckodriver v0.24.0](https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-win64.zip)
* Create a folder in **C:/Users/YOUR_USER/AppData/** and name it as **Geckodriver**
* Extract the **geckodriver.exe** in the ZIP file from the step below and put it in the folder Geckodriver

![Example Geckodriver directory path](/images/example-01.png)

* Open the command prompt and paste fhe following command
```bash
setx path "%path%;C:\Users\YOUR_USER\AppData\Local\Geckodriver"
```
* This command will set the Geckodriver directory in your environment variables
* Restart your computer
* Test the script
