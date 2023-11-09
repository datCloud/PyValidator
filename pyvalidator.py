from __future__ import print_function, unicode_literals
from requests_html import HTMLSession
from tqdm import tqdm
import time
import os
import inspect
import errno
import socket
import json
from colorama import Fore, Back, Style
from selenium import webdriver
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys
import base64
from pyfiglet import Figlet
import re

from socket import error as socket_error
from selenium.common.exceptions import UnexpectedAlertPresentException
from requests.exceptions import MissingSchema, InvalidSchema, ConnectTimeout

import requests
import xmltodict

import git
import urllib3

import subprocess
import pkgutil

from pprint import pprint
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

from PIL import Image
import io

# from py_validator_lang import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def repo_is_up_to_date():
    repo = git.Repo(search_parent_directories=True)
    repo.remotes.origin.fetch()
    commits_behind = repo.iter_commits('master..origin/master')
    commits_ahead = repo.iter_commits('origin/master..master')
    count_behind = sum(1 for c in commits_behind)

    if(count_behind > 0):
        print(f'{Fore.YELLOW}There are new commits on remote repository\nTo continue using PyValidator you need to updated it{Style.RESET_ALL}')
        quit()

try:

    use_ssl = False
    vnu_port = 4242

    mpis_links_file = 'mpis.txt'
    
    repo_is_up_to_date()

    style = style_from_dict({
        Token.QuestionMark: '#ff00ff bold',
        Token.Selected: '#0000ff bold',
        Token.Instruction: '#ff0000',  # default
        Token.Answer: '#00ff00 bold',
        Token.Question: '',
    })

    class UrlValidator(Validator):
        def validate(self, document):
            # ok = re.match('^([a-z\-]{3,}\.[a-z\-]{3,}(?:[\.]?[a-z]{3,})?(?:[\.]?[a-z]{2,})?)', document.text)
            if not re.match('^(?:www\.)?([\w-]+\.[\w.-]+)$', document.text):
                raise ValidationError(
                    message='Enter a valid domain',
                    cursor_position=len(document.text))  # Move cursor to end

    questions = [
        {
            'type': 'confirm',
            'name': 'validation_upsell',
            'message': 'Is a MPI upsell?',
            'default': False
        },
        {
            'type': 'checkbox',
            'message': 'What do you want to validate?',
            'name': 'validation_params',
            'choices': [
                {
                    'name': 'W3C issues (Powered by w3c.org)',
                    'value': 'w'
                },
                {
                    'name': 'SEO structure for Alt and Title attributes',
                    'value': 's'
                },
                {
                    'name': 'Validate MPIs',
                    'value': 'm'
                },
                {
                    'name': 'Mobile (Content width)',
                    'value': 'l'
                },
                {
                    'name': 'Pagespeed (Home and one random MPI)',
                    'value': 'p'
                }
            ],
            'when': lambda answers: answers['validation_upsell'] == False
        },
        {
            'type': 'list',
            'name': 'validation_crawler_mode',
            'message': 'Choose the crawler mode:',
            'choices': ['Default crawler', 'Use sitemap.xml', 'Use local file'],
            'default': 'Default crawler',
            'when': lambda answers: answers['validation_upsell'] == False
        },
        {
            'type': 'list',
            'name': 'validation_local',
            'message': 'What\'s your server project?',
            'choices': ['Produção', 'Contenção', 'Growth', 'Publicado'],
        },
        {
            'type': 'input',
            'name': 'validation_url',
            'message': 'What\'s the project url? Ex.: site.com.br or www.site.com.br',
            'validate': UrlValidator
        },
        {
            'type': 'confirm',
            'name': 'validation_export',
            'message': 'Want to export all crawled links?',
            'default': False,
            'when': lambda answers: answers['validation_upsell'] == False
        }
    ]

    notForRobots = ['mpitemporario', 'localhost']

    mpiRules = {
        'h2Count': 1,
        'imageCount': 1,
        'descriptionRange': [140, 160],
        'keywordPositionInDescription': 19,
        'strongCount': 3
    }

    ext_mime = {
        'jpg': 'JPEG',
        'jpeg': 'JPEG',
        'png': 'PNG',
        'webp': 'WEBP',
        'gif': 'GIF',
        'svg': 'SVG'
    }

    def check_robots(str):
        canCheckRobots = False

        for ignoreRobotsItem in notForRobots:
            if ignoreRobotsItem in url:
                canCheckRobots = True
                break

        if canCheckRobots:
            r = session.get(url + 'robots.txt', headers = defaultHeader, verify = use_ssl)
            robots = r.text
            if url not in robots:
                print('Robots -> Wrong')

    def format_url(url, location):
        return f'www.{url}' if not url.startswith('www.') and location == '' else url

    def format_validation_string(answers_list):
        protocol = 'https://'
        local = {
            'Produção': 'producao.mpitemporario.com.br/',
            'Contenção': 'mpitemporario.com.br/projetos/',
            'Growth': 'growth.mpitemporario.com.br/',
            'Publicado': ''
        }
        mode = {
            'Default crawler': '',
            'Use sitemap.xml': ' -x',
            'Use local file': ' -f'
        }

        try:
            current_mode = mode[answers_list['validation_crawler_mode']]
        except KeyError:
            current_mode = ''

        choosed_local = local[answers_list['validation_local']]
        current_url = format_url(answers_list['validation_url'], choosed_local)

        try:
            current_params = ' '.join([f'-{p}' for p in answers_list['validation_params']])
        except KeyError:
            current_params = ' -is_upsell'

        try:
            will_export = ' -e' if answers_list['validation_export'] == True else ''
        except KeyError:
            will_export = ''

        return f'{protocol}{choosed_local}{current_url}/ {current_params}{will_export}{current_mode}'

    def check_gh_token():
        try:
            userDataFile = open(os.path.join(currentDirectory, 'user.auth'), 'r', encoding='utf-8')
            userDataList = []

            for line in userDataFile:
                userDataList.append(line)

            ghToken = base64.b64decode(userDataList[0]).decode()
        except:
            print(f'{Fore.YELLOW}In order to use this tool you need to enter a valid personal token for GitHub API.\nFor more info access {Style.RESET_ALL}https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token\n')
            ghToken = input('Enter your GH_TOKEN: ')

            userDataFile = open(os.path.join(currentDirectory, 'user.auth'), 'w+', encoding='utf-8')
            userDataFile.write(f'{base64.b64encode(ghToken.encode()).decode()}')
            userDataFile.close()

        return ghToken

    currentDirectory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    os.environ['GH_TOKEN'] = check_gh_token()

    f = Figlet(font='slant')

    ignoreLinksWith = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '?', '#', '.pdf', 'tel:', 'mailto:', '.mp4', '.webm', '.zip', '.rar', '.exe', '.xls', '.xls', '.doc']

    os.system('clear')
    print(Fore.YELLOW)
    print(f.renderText('PyValidator'))
    print(f'(by datCloud)\n')
    print(Style.RESET_ALL)

    answers = prompt(questions, style=style)
    url = format_validation_string(answers)
    # print(url)
    # quit()

    url_first_part = url.split('//')[1].split('/')[0]

    def read_json_from_url(url):
        response = requests.get(url) 
        return response.json()

    def w3c_validation(url, port):
        vnu_json = read_json_from_url(f'http://localhost:{port}/?out=json&doc={url}')
        if(vnu_has_errors(vnu_json)):
            print(f'\n{Fore.YELLOW}{Style.BRIGHT}W3C Issues:{Style.RESET_ALL}\n\t{Style.BRIGHT}Origin:{Style.RESET_ALL} {url}\n\t{Style.BRIGHT}Report:{Style.RESET_ALL} http://localhost:{port}/?doc={url}')
    
    def vnu_has_errors(json_obj):
        for msg in json_obj['messages']:
            try:
                if msg['subType'] in ['warning']: return True
            except: pass
        return False if len(json_obj['messages']) == 0 else not all(msg['type'] in ['info'] for msg in json_obj['messages'])

    def get_package_path(package_name):
        loader = pkgutil.find_loader(package_name)
        if loader is None:
            print(f'No module "{package_name}" found.\nTo fix run:\n\tpip install py-html-checker[cli,jinja]')
            quit()

        elif hasattr(loader, 'get_filename'):
            # Installed via pip or similar 
            return loader.get_filename(package_name)

        elif hasattr(loader, 'get_data'):
            # For packages in current directory or PYTHONPATH
            return loader.get_data(package_name).__file__

    def is_port_free(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result

    def serve_nu_validator(port):
        if(is_port_free(port)):
            process = subprocess.Popen(f'java -cp ./vnu/vnu.jar nu.validator.servlet.Main {port}', creationflags = subprocess.CREATE_NO_WINDOW)
        else:
            print(f'{Fore.YELLOW}Nu Html Checker already running locally{Style.RESET_ALL}')
        print(f'{Fore.YELLOW}Access local instance of Nu Html Checker at {Style.RESET_ALL}{Style.BRIGHT}http://localhost:{port}{Style.RESET_ALL}')

    def get_url(urlInput):
        urlInput = urlInput.split(' ')[0]
        return urlInput if urlInput[-1:] == '/' else urlInput + '/'

    vPagespeed = True if ' -p' in url else False
    vW3C = True if ' -w' in url else False
    vSEO = True if ' -s' in url else False
    vMPI = True if ' -m' in url else False
    vUniqueLinks = True if ' -u' in url else False
    vMobile = True if ' -l' in url else False
    vAll = True if ' -a' in url else False
    vSitemap = True if ' -x' in url else False
    vDebug = True if ' -d' in url else False
    vFile = True if ' -f' in url else False
    vExport = True if ' -e' in url else False
    vUpsell = True if ' -is_upsell' in url else False

    if vAll:
        vPagespeed = True
        vW3C = True
        vSEO = True
        vMPI = True
        # vUniqueLinks = True
        vMobile = True

    vImageData = False

    url = get_url(url)
    baseUrl = url

    defaultHeader = {
        'user-agent':'Mozilla/5.0',
        'x-requested-with': 'XMLHttpRequest',
        'ngrok-skip-browser-warning': '42'
    }

    def valid_url(url):
        url = url.lower()
        return False if any(ext in url for ext in ignoreLinksWith) else True

    serve_nu_validator(vnu_port)

    session = HTMLSession()
    try:
        r = session.get(url, headers = defaultHeader, verify = use_ssl)
    except:
        use_ssl = True
        try:
            r = session.get(url, headers = defaultHeader, verify = use_ssl)
        except ConnectTimeout:
            print(f'Cannot establish connection')
            quit()

    insideLinks = r.html.xpath('//a[not(@rel="nofollow")]')
    menuTop = r.html.absolute_links

    hasSitemap = False

    imageList = []

    check_robots(url)

    if vMobile or vUpsell:
        
        set_device_metrics_override = dict({
            "width": 320,
            "height": 568,
            "deviceScaleFactor": 50,
            "mobile": True
        })
        
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
        
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument(f'--user-agent="{user_agent}"')
        driver_options.add_argument("--headless")
        driver_options.add_argument("--disable-gpu")
        driver_options.add_argument("--log-level=3")
        driver_options.add_argument("start-maximized")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=driver_options)
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', set_device_metrics_override)

    def get_mobile_width(pageUrl):
        try:
            driver.get(pageUrl)
            windowWidth = driver.execute_script('return document.body.clientWidth')
            documentWidth = driver.execute_script('return document.body.scrollWidth')
            if windowWidth < documentWidth:
                print(f'\n{Fore.YELLOW}{Style.BRIGHT}Mobile issue:{Style.RESET_ALL}\n\t{Style.BRIGHT}Window width:{Style.RESET_ALL} {windowWidth}\n\t{Style.BRIGHT}Document width:{Style.RESET_ALL} {documentWidth}\n\t{Style.BRIGHT}Origin:{Style.RESET_ALL} {pageUrl}')
        except UnexpectedAlertPresentException:
            print(f'\n{Fore.YELLOW}{Style.BRIGHT}Page shows alert{Style.RESET_ALL}\n\t{Style.BRIGHT}Origin:{Style.RESET_ALL} {pageUrl}')


    def check_duplicated_mpis(mpiLinks):
        allMPILinks = set()
        duplicatedMPILinks = [x for x in mpiLinks if x in allMPILinks or allMPILinks.add(x)]
        if duplicatedMPILinks:
            print(f'\n{Fore.YELLOW}{Style.BRIGHT}Duplicated MPIs:{Style.RESET_ALL}')
            for duplicatedMPI in duplicatedMPILinks:
                print(f'\t{duplicatedMPI}')
            print(f'\n')
            return duplicatedMPILinks
        return False

    def is_icm(response, mpiLink):
        return True if response.html.find('body.mpi-rules', first = True) else False

    def check_status_code(response, link):
        code = response.status_code
        if code != 200:
            print(f'\n{Back.RED}{Style.BRIGHT}Link redirects to {code}:{Style.RESET_ALL} {link}')
            return False
        return True

    def check_issues(mpiLinks):
        issueUrls = []
        for link in tqdm(mpiLinks):
            if vDebug: print(link)
            issueMessages = []
            r = session.get(link, headers = defaultHeader, verify = use_ssl)
            if not check_status_code(r, link): continue
                
            mpiElement = r.html.find('ul.thumbnails, .card, .card--mpi', first = True)
            if mpiElement: continue

            ignore_strong = True if r.html.find('body[data-no-strong]', first = True) else False

            try:
                description = r.html.find('head meta[name="description"]', first=True).attrs['content']
            except:
                print(f'{Fore.YELLOW}{Style.BRIGHT}MPI issue:{Style.RESET_ALL}\n\tCannot find meta tag description from {link}')
                continue
            images = len(r.html.find('ul[class$="gallery"] img'))
            if images == 0:
                try:
                    images = len(r.html.find('article img'))
                except:
                    pass

            h2 = r.html.find('article h2')
            articleElements = r.html.find('article h2, article p, article ul.list li')
            strongsInArticle = len(r.html.find('article strong'))
            titleWithStrong = r.html.find('article h2 strong')
            allParagraphs = r.html.find('article p, article ul.list li')

            try:
                h1 = r.html.find('h1')
                if(len(h1) > 1):
                    issueMessages.append('There is more than 1 H1')
                h1 = h1[0].text
            except AttributeError as aerr:
                issueMessages.append('There is no H1')
                continue

            h2HasH1 = False
            for uniqueH2 in h2:
                if h1.lower() in uniqueH2.text.lower():
                    h2HasH1 = True
                    break

            h2List = []
            for title in h2:
                h2List.append(title.text)
                if title.text.lower() == h1.lower():
                    issueMessages.append('There are H2 equals to H1')
                    break

            if len(h2List) != len(set(h2List)):
                issueMessages.append('There are duplicated H2')

            descriptionInArticle = False
            if len(description) > 30:
                for paragraph in allParagraphs:
                    if paragraph.text != '': # remove
                        if description[:-20].lower().strip() in paragraph.text.lower() and not descriptionInArticle:
                            descriptionInArticle = True
                            break

            if not descriptionInArticle:
                issueMessages.append('Description not in article')

            if len(allParagraphs) != len(set(allParagraphs)):
                issueMessages.append('There are duplicated paragraphs')

            emptyElements = []
            for emptyElement in articleElements:
                if len(emptyElement.text.strip()) < 2:
                    emptyElements.append(emptyElement)

            fakeTitles = r.html.find('article p')
            pUpper = []
            for fakeTitle in fakeTitles:
                if fakeTitle.text.isupper():
                    pUpper.append(fakeTitle)
            
            sequentialList = r.html.find('article ul + ul')
            sequentialTitle = r.html.find('article h2:not([data-tab]) + h2')

            if h1.lower() not in description.lower() : 
                issueMessages.append('Description doesn\'t have mention to H1')
            elif description.lower().find(h1.lower()) > mpiRules['keywordPositionInDescription']:
                issueMessages.append('H1 not in first 20 chars of description')
            if strongsInArticle < mpiRules['strongCount'] and not ignore_strong:
                issueMessages.append(f'There are only {strongsInArticle} strongs in this article')
            if len(titleWithStrong) > 0:
                issueMessages.append(f'There are {len(titleWithStrong)} titles with strong in this article')
            if len(pUpper) > 0:
                issueMessages.append(f'There are {len(pUpper)} uppercase p')
            if len(emptyElements) > 0:
                issueMessages.append(f'There are {len(emptyElements)} empty elements')
            if len(description) < mpiRules['descriptionRange'][0] or len(description) > mpiRules['descriptionRange'][1] : 
                issueMessages.append(f'Description char count: {len(description)}')
            if images < mpiRules['imageCount'] :
                issueMessages.append(f'Image count: {images}')
            if len(h2) < mpiRules['h2Count'] :
                issueMessages.append(f'H2 count: {len(h2)}')
            if not h2HasH1:
                issueMessages.append(f'H2 text doesn\'t have mention to H1 in')
            if len(sequentialList) > 0 :
                issueMessages.append(f'There are {len(sequentialList)} list(s) in sequence')
            if len(sequentialTitle) > 0 :
                issueMessages.append(f'There are {len(sequentialTitle)} title(s) in sequence')
            if len(issueMessages) > 0 :
                print(f'\n{Fore.YELLOW}{Style.BRIGHT}MPI issues:{Style.RESET_ALL}')
                for issue in issueMessages:
                    print(f'\t{issue}')

                print(f'\t{Fore.YELLOW}{Style.BRIGHT}Origin: {Style.RESET_ALL}{link}')
        print('-------------- MPI Validation Finished --------------')
        if not vW3C and not vSEO and not vMobile and not vUpsell:
            sys.exit('Finished')

    def page_speed(pagespeedUrl, apiKey):

        print(f'{pagespeedUrl}')
        
        mobileUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=mobile&key={apiKey}'
        desktopUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=desktop&key={apiKey}'

        mobileRequest = session.get(mobileUrl, headers = defaultHeader, verify = use_ssl)
        jsonData = json.loads(mobileRequest.text)
        mobileScore = int(float(jsonData['lighthouseResult']['categories']['performance']['score']) * 100)
        print(f'Mobile score - {mobileScore}')

        desktopRequest = session.get(desktopUrl, headers = defaultHeader, verify = use_ssl)
        jsonData = json.loads(desktopRequest.text)
        desktopScore = int(float(jsonData['lighthouseResult']['categories']['performance']['score']) * 100)
        print(f'Desktop score - {desktopScore}')
        print('-' * 40)

    def has_event_listener(elem):
        try:
            return 'doGTranslate' in elem.attrs['onclick']
        except KeyError:
            return False

    def count_protocol(elem):
        try:
            return elem.attrs['href'].count('://') > 1
        except KeyError:
            return False

    def ends_with_hash(elem):
        try:
            return re.search(r".*#$", elem.attrs['href'])
        except KeyError:
            return False

    def site_urls(insideLinks, hasSitemap, current_link):
        if vSitemap:
            sitemapUrl = url + 'sitemap.xml'
            sitemapRequest = requests.get(sitemapUrl, headers = defaultHeader, verify = use_ssl)
            sitemapLinks = []
            try:
                sitemapContent = xmltodict.parse(sitemapRequest.content)
                for sitemapItem in sitemapContent['urlset']['url']:
                    if sitemapItem['loc'] in sitemapLinks:
                        print(f'{Fore.YELLOW}\nDuplicated link in sitemap.xml: {Style.RESET_ALL}{sitemapItem.text}\n')
                        continue
                    sitemapLinks.append(sitemapItem['loc'])
            except:
                pass
            if len(sitemapLinks) > 0:
                for sitemapLink in sitemapLinks:
                    if '.pdf' not in sitemapLink and 'tim.php' not in sitemapLink and 'thumbs.php' not in sitemapLink:
                        visitedLinks.append(sitemapLink)
                if url + '404' in visitedLinks:
                    print('Found 404 link in sitemap.xml')
                return 0
            elif not hasSitemap:
                print('The site doesn\'t have a sitemap.xml file')
                print('Getting links...')
                hasSitemap = True
        for link in insideLinks:
            if count_protocol(link) or (ends_with_hash(link) and not has_event_listener(link)):
                print(f'{Fore.RED}{Style.BRIGHT}Incorrect link{Style.RESET_ALL}\n\t{Style.BRIGHT}Link:{Style.RESET_ALL} {link.attrs["href"]}\n\t{Style.BRIGHT}Origin:{Style.RESET_ALL} {current_link}')
            try:
                if 'http' in link.attrs['href'] and url_first_part in link.attrs['href']:
                    if valid_url(link.attrs['href']):
                        links.append(link.attrs['href'])
            except KeyError:
                pass
        for link in links:
            if link not in visitedLinks:
                if link[-1:] == '/' and link != baseUrl : continue
                if 'orcamento' in link: continue
                visitedLinks.append(link)
                try:
                    r = session.get(link, headers = defaultHeader, verify = use_ssl)
                except:
                    print(f'Cannot access {link}')
                    pass
                if not check_status_code(r, link):
                    inaccessibleLinks.append(link)
                    continue
                pageLinks = r.html.xpath('//a[not(@rel="nofollow")]')
                site_urls(pageLinks, hasSitemap, link)

    def check_for_unique_links(uniqueLinks):
        r = session.get(url + '/mapa-site', headers = defaultHeader, verify = use_ssl)
        sitemapElements = r.html.find('.sitemap li a')
        sitemapLinks = []
        unlistedLinks = []
        for sitemapElement in sitemapElements:
            sitemapLinks.append(sitemapElement.attrs['href'])
        for uniqueLink in uniqueLinks:
            if uniqueLink not in sitemapLinks and '/mapa-site' not in uniqueLink and '/carrinho' not in uniqueLink:
                unlistedLinks.append(uniqueLink)
        if(len(unlistedLinks) > 0):
            print(f'These links are not listed in sitemap page')
            for unlistedLink in unlistedLinks:
                print(unlistedLink)
            print('------------------------')

    def remove_links(linksList, removeLinks):
        for link in removeLinks:
            linksList.remove(link)
        return linksList
        
    # Check if page mentions "Doutores da Web"

    def has_default_text(r, link):
        try:
            if 'doutores da web' in r.html.find('body', first = True).text.lower():
                print(f'{Fore.YELLOW}{Style.BRIGHT}Content mentions "Doutores da Web"\n\tOrigin:{Style.RESET_ALL} {link}')
        except:
            print_seo_alerts('Page has no body', link, r.html)                

    def print_seo_alerts(title, link, ref):
        text_style = f'{Fore.YELLOW}{Style.BRIGHT}'
        print(f'\n{text_style}{title}\n\tOrigin: {Style.RESET_ALL}{link}\n\t{text_style}Reference: {Style.RESET_ALL}{ref}')

    def get_img_ext(src):
        regex = r'\.(jpg|jpeg|png|webp|gif|svg)\b'
        match = re.search(regex, src, re.IGNORECASE)
        return match.group(1) if match else None

    def is_banner(src):
        return True if '/slider/' in src or '/banner/' in src else False

    def image_validation(img_src, link):
        if('solucoesindustriais.com.br' in img_src): return
        try:
            img_response = requests.get(img_src)
        except (MissingSchema, InvalidSchema):
            print_seo_alerts(f'Incorrect url', link, img_src)
            return
        except ConnectTimeout:
            print_seo_alerts(f'Connection timeout', link, img_src)
            return
        img_data = img_response.content
        img_ext = get_img_ext(img_src)
        if img_ext != 'svg':
            try:
                img = Image.open(io.BytesIO(img_data))
            except:
                print_seo_alerts(f'(PROBABLY) Broken image', link, img_src)
                return
            width, height = img.size
            img_mime = img.format
            if (width > 800 or height > 800) and not is_banner(img_src): print_seo_alerts(f'Image dimensions: {width}x{height}', link, img_src)
        else:
            img_mime = 'SVG'
        try:
            if ext_mime.get(img_ext) != img_mime: print_seo_alerts(f'Image extension x MIME: {img_ext.upper()} x {img_mime}', link, img_src)
        except AttributeError:
            print_seo_alerts(f'Cannot get image extension', link, img_src)
        if len(img_data)/1024 > 200 or (is_banner(img_src) and len(img_data)/1024 > 400): print_seo_alerts(f'Image filesize: {round(len(img_data)/1024, 2)}', link, img_src)

    # SEO Validation function

    def seo_validation(r):
        allImages = r.html.find('body img')
        allLinks = r.html.find('body a[href*="http"]')
        try:
            h1 = r.html.find('h1')
            if len(h1) > 1:
                print(f'\n{Fore.RED}{Style.BRIGHT}Multiple H1 found{Style.RESET_ALL}\n\t{Fore.YELLOW}{Style.BRIGHT}Origin:{Style.RESET_ALL} {link}')
                return
            h1 = h1[0].text
        except (AttributeError, IndexError):
            print(f'\n{Fore.RED}{Style.BRIGHT}H1 not found{Style.RESET_ALL}\n\t{Fore.YELLOW}{Style.BRIGHT}Origin:{Style.RESET_ALL} {link}')
            return

        try:
            hidden_h1 = r.html.find('h1', first=True).attrs['hidden']
            if(hidden_h1): print(f'\n{Fore.RED}{Style.BRIGHT}H1 with hidden attribute{Style.RESET_ALL}')
        except:
            pass


        description_element = r.html.find('head meta[name="description"]', first=True)
        description_content = description_element.attrs['content']

        if h1.lower() not in description_content.lower() and link.split(answers['validation_url'])[1] != url.split(answers['validation_url'])[1]:
            print_seo_alerts('Description doesn\'t have mention to H1', link, description_element)
        if len(description_content) < 140 or len(description_content) > 160 : 
            print(f'\nDescription char count: {len(description_content)} \n in {link}')
        for current_image in allImages:
            try:
                img_src = current_image.attrs['src'] if current_image.attrs['src'] != '#' else current_image.attrs['data-lazy']
                image_validation(img_src, link)
            except KeyError as err:
                print_seo_alerts('Image without src', link, current_image.html)
            try:
                if 'escrev' in current_image.attrs['title'].lower() or 'doutores da web' in current_image.attrs['title'].lower() or current_image.attrs['title'].strip() == '':
                    print_seo_alerts('Wrong title', link, current_image.html)
            except KeyError as err:
                print_seo_alerts('Image without title', link, current_image.html)
            try:
                if 'escrev' in current_image.attrs['alt'].lower() or 'doutores da web' in current_image.attrs['alt'].lower() or current_image.attrs['alt'].strip() == '' :
                    print_seo_alerts('Wrong alt', link, current_image.html)
            except KeyError as err:
                print_seo_alerts('Image without alt', link, current_image.html)
        for checkLink in allLinks:
            try:
                if 'facebook' in checkLink.attrs['href'].lower():
                    continue
                if 'escrev' in checkLink.attrs['title'].lower() or 'doutores da web' in checkLink.attrs['title'].lower() or checkLink.attrs['title'] == '':
                    opening_tag_link = checkLink.html.split('>')[0] + '>'
                    print_seo_alerts('Link with wrong title', link, opening_tag_link)
            except KeyError as err:
                opening_tag_link = checkLink.html.split('>')[0] + '>'
                print_seo_alerts('Link without title', link, opening_tag_link)

    # First check

    try:
        r = session.get(url, headers = defaultHeader, verify = use_ssl)
    except:
        print(f'Cannot access {url}')
        quit()
    if not check_status_code(r, url):
        quit()

    # Get MPI Links

    if vMPI or vUpsell:
        r = session.get(f'{url}mapa-site', headers = defaultHeader, verify = use_ssl)

        mpi_list = r.html.find('header a[data-mpi]')
        if len(mpi_list) == 0:
            mpi_list = r.html.find('.sitemap ul.sub-menu-info li a')
        mpiLinks = []
        mpi_questions = [
            {
                'type': 'confirm',
                'name': 'mpi_from_file',
                'message': 'Get links from mpi.txt?',
                'default': False
            }
        ]

        while len(mpi_list) == 0 and len(mpiLinks) == 0:
            if os.path.isfile(mpis_links_file):
                os.remove(mpis_links_file)
            open(mpis_links_file, 'w', encoding='utf-8').close()
            print(f'{Back.RED}{Style.BRIGHT}No MPIs found in this project\nMake sure the submenu with the MPIs has the class sub-menu-info\nYou can fill the mpi.txt file to continue{Style.RESET_ALL}')
            mpi_answer = prompt(mpi_questions, style=style)
            if mpi_answer['mpi_from_file'] == False:
                raise KeyboardInterrupt
            with open(os.path.join(currentDirectory, mpis_links_file), 'r', encoding='utf-8') as file:
                mpiLinks = file.read().splitlines()
        
        if len(mpiLinks) == 0:
            for content in mpi_list:
                mpiLinks.append(str(content.links)[2:-2])

        if vExport:
            mpiListFile = open(os.path.join(currentDirectory, 'links.txt'), 'w+', encoding='utf-8')
            for mpiLink in mpiLinks:
                mpiListFile.write(f'{mpiLink}\n')
            mpiListFile.close()

        print('-------------- MPI Validation --------------')
        check_duplicated_mpis(mpiLinks)  
        check_issues(mpiLinks)

    # Define a list that will receive all links

    links = []
    visitedLinks = [url]

    inaccessibleLinks = []

    # PageSpeed

    if vPagespeed:

        pageSpeedLinks = [url]

        if(len(mpiLinks) > 0):
            pageSpeedLinks.append(random.choice(mpiLinks))
        
        print('-------------- PageSpeed Insights --------------')
        print('Checking PageSpeed Score...')

        apiKey = 'AIzaSyDFsGExCkww5IFLzG1aAnfSovxSN-IeHE0'

        for pageSpeedLink in pageSpeedLinks:
            page_speed(pageSpeedLink, apiKey)

    if vFile:
        try:
            with open(os.path.join(currentDirectory, 'links.txt'), 'r', encoding='utf-8') as file:
                links_from_file = file.read().splitlines()
                visitedLinks = list(filter(lambda x: not x.endswith('.pdf'), links_from_file))
        except:
            print(f'File not found\n')
            vFile = False

    # Crawls links from site

    if (vW3C or vSEO or vMobile) and not vFile:
        site_urls(insideLinks, hasSitemap, url)
        visitedLinks = remove_links(visitedLinks, inaccessibleLinks)

    if vUpsell:
        visitedLinks = mpiLinks    

    # Check for links that aren't in main menu

    if vUniqueLinks:
        check_for_unique_links(visitedLinks)

    # Mobile, SEO and W3C validations

    if vW3C or vSEO or vMobile or vUpsell:
        visitedLinks = list(set(visitedLinks))
        if url[:-1] in visitedLinks:
            visitedLinks.remove(url[:-1])
        if url[:-1].replace('://', '://www.') in visitedLinks:
            visitedLinks.remove(url[:-1].replace('://', '://www.'))
        for link in tqdm(visitedLinks):
            if vDebug: print(link)
            r = session.get(link, headers = defaultHeader, verify = use_ssl)
            has_default_text(r, url)
            if not check_status_code(r, link):
                inaccessibleLinks.append(link)
                continue
            if vMobile or vUpsell:
                get_mobile_width(link)
            if vSEO or vUpsell:
                seo_validation(r)
            if vW3C or vUpsell:
                w3c_validation(link, vnu_port)

    if vMobile or vUpsell:
        driver.close()
        driver.quit()

    print('Finished')

except KeyboardInterrupt:
    print('Interrupting validation')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
