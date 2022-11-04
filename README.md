# PyValidator [![Licensed under the MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/datCloud/PyValidator/blob/master/LICENSE)
Python website validator. Checks W3C, PageSpeed, SEO, Mobile, etc

## Prerequisites
### Install Python 3.7.4+
* [Download and install Python 3.7.4+ for Windows](https://www.python.org/downloads/)
* Before install it, **remember to check 'Add Python 3.x to PATH'** box on instalation window
### Python packages
* On your command prompt, run the following commands:
```bash
pip install selenium
pip install requests_html
pip install colorama
pip install tqdm
pip install webdriver_manager
pip install pyfiglet
```
### Install Mozilla Firefox
This tool uses Mozilla Firefox browser with Selenium for Mobile validation

Download the latest version of [Mozilla Firefox](https://www.mozilla.org/pt-BR/firefox/new/)
### GH_TOKEN
The PyValidator uses webdriver_manager to get the latest version of Geckodriver via GitHub API.

In order for it to be downloaded properly, on your first run, the PyValidator will request the GH_TOKEN.

To generate the token follow [Creating a fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token) instructions on GitHub Docs.

Just copy and paste it into the command prompt.
## Basic usage
Run the **pyvalidator.py** script on your command prompt and paste the url of the website you want to validate
There are several options to validate and you may enter them as arguments after the url:
* ```-w``` W3C issues (Powered by [w3c.org](https://www.w3.org/))
* ```-s``` SEO structure for Alt and Title attributes
* ```-m``` Check MPI model and validade all MPIs 
* ```-l``` Check lateral scroll on mobile
* ```-x``` Use sitemap.xml to get site links (crawls faster)
* ```-p``` Pagespeed score for the home page
* ```-u``` Search for links that aren\'t in the menu
* ```-c``` Compare top and footer menus (Old websites)
* ```-a``` Check all errors
### If you have any issue, please let me know :wink:
