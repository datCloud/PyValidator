from requests_html import HTMLSession
from tqdm import tqdm
import time
import os
import inspect
import errno
import socket
from socket import error as socket_error
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

import requests
import xmltodict

import git
import urllib3

import subprocess
import pkgutil

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
    
    repo_is_up_to_date()

    notForRobots = ['mpitemporario', 'localhost']

    mpiRules = {
        'h2Count': 1,
        'imageCount': 1,
        'descriptionRange': [140, 160],
        'keywordPositionInDescription': 19,
        'strongCount': 3
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

    url = ''

    tries = 0

    def input_validation(str):
        if ' -' not in str: return True
        if str.split(' -')[0].split('/')[-1] != '': return True
        return False


    while input_validation(url):
        os.system('clear')
        print(Fore.YELLOW)
        print(f.renderText('PyValidator'))
        print(f'(by datCloud)\n')
        print('----------------------------------')
        print('|          INSTRUCTIONS          |')
        print('----------------------------------')
        print('\nPaste the site URL followed by desired parameters\n')
        print('-w ------- W3C issues (Powered by w3c.org)')
        print('-s ------- SEO structure for Alt and Title attributes')
        print('-m ------- Check MPI model and validade all MPIs ')
        print('-l ------- Check lateral scroll on mobile')
        print('-x ------- Use sitemap.xml to get site links (crawls faster)')
        print('-p ------- Pagespeed score for the home page')
        print('-u ------- Search for links that aren\'t in the menu')
        print('-c ------- Compare top and footer menus (Old websites)')
        print('-a ------- Check all errors')
        print('-d ------- Show links while validate')
        print('-e ------- Export crawled link (usefull for upsells)')
        print('-f ------- Get links from links.txt')
        print('\nExample: [url] [parameter] [...]', Style.RESET_ALL)
        tries += 1
        if tries > 3: print(f'\n{Back.RED} TRY SOMETHING LIKE THIS, BRO ¬¬ \n https://domain.com.br/ -w -s {Style.RESET_ALL}')
        url = input(str('\nPaste the url here: '))

    url_first_part = url.split('//')[1].split('/')[0]

    def read_json_from_url(url):
        response = requests.get(url) 
        return response.json()

    def w3c_validation(url, port):
        vnu_json = read_json_from_url(f'http://localhost:{port}/?out=json&doc={url}')
        if(vnu_has_errors(vnu_json)):
            print(f'\n{Fore.YELLOW}{Style.BRIGHT}W3C Issues:{Style.RESET_ALL}\n\t{Style.BRIGHT}Origin:{Style.RESET_ALL} {url}\n\t{Style.BRIGHT}Report:{Style.RESET_ALL} http://localhost:{port}/?doc={url}')
    
    def vnu_has_errors(json_obj):
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
    vMapaSite = True if ' -z' in url else False
    vDebug = True if ' -d' in url else False
    vFile = True if ' -f' in url else False
    vExport = True if ' -e' in url else False

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
        r = session.get(url, headers = defaultHeader, verify = use_ssl)

    insideLinks = r.html.xpath('//a[not(@rel="nofollow")]/@href')
    menuTop = r.html.absolute_links

    hasSitemap = False

    imageList = []

    check_robots(url)

    if vMobile:
        
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
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="114.0.5735.90").install()), options=driver_options)
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', set_device_metrics_override)

    def get_mobile_width(pageUrl): 
        driver.get(pageUrl)
        windowWidth = driver.execute_script('return document.body.clientWidth')
        documentWidth = driver.execute_script('return document.body.scrollWidth')
        if windowWidth < documentWidth:
            print(f'\n{Fore.YELLOW}{Style.BRIGHT}Mobile issue:{Style.RESET_ALL}\n\t{Style.BRIGHT}Window width:{Style.RESET_ALL} {windowWidth}\n\t{Style.BRIGHT}Document width:{Style.RESET_ALL} {documentWidth}\n\t{Style.BRIGHT}Origin:{Style.RESET_ALL} {pageUrl}')

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
        mpiStyle = None
        for link in tqdm(mpiLinks):
            if vDebug: print(link)
            issueMessages = []
            r = session.get(link, headers = defaultHeader, verify = use_ssl)
            if not check_status_code(r, link): continue
            if mpiStyle is None:
                mpiStyle = is_icm(r, mpiLinks[0])
                
            mpiElement = r.html.find('ul.thumbnails, .card, .card--mpi', first = True)
            if mpiElement: continue

            try:
                description = r.html.find('head meta[name="description"]', first=True).attrs['content']
            except:
                print(f'{Fore.YELLOW}{Style.BRIGHT}MPI issue:{Style.RESET_ALL}\n\tCannot find meta tag description from {link}')
                continue
            images = len(r.html.find('ul.gallery img'))
            if images == 0:
                try:
                    images = len(r.html.find('article:first img'))
                except:
                    pass
            if mpiStyle:
                h2 = r.html.find('article:first h2')
                articleElements = r.html.find('article:first h2, article:first p, article:first ul.list li')
                strongsInArticle = r.html.find('article:first strong')
                titleWithStrong = r.html.find('article:first h2 strong')
                allParagraphs = r.html.find('article:first p, article:first ul.list li')
            else:
                h2 = r.html.find('article h2')
                articleElements = r.html.find('article h2, article p, article ul.list li')
                strongsInArticle = r.html.find('article strong')
                titleWithStrong = r.html.find('article h2 strong')
                allParagraphs = r.html.find('article p, article ul.list li')

            hasIssues = False

            try:
                h1 = r.html.find('h1')
                if(len(h1) > 1):
                    issueMessages.append('There is more than 1 H1')
                    hasIssues = True
                h1 = h1[0].text
            except AttributeError as aerr:
                h1 = 'Not found'
                issueMessages.append('There is no H1')
                hasIssues = True
                continue

            h2HasH1 = False
            for uniqueH2 in h2:
                if h1.lower() in uniqueH2.text.lower():
                    h2HasH1 = True
                    break

            h2List = []
            h1EqualsH2 = False
            for title in h2:
                h2List.append(title.text)
                if title.text.lower() == h1.lower() and not h1EqualsH2:
                    issueMessages.append('There are H2 equals to H1')
                    hasIssues = True
                    h1EqualsH2 = True

            if len(h2List) != len(set(h2List)):
                issueMessages.append('There are duplicated H2')
                hasIssues = True

            pAllList = []
            descriptionInArticle = False
            for paragraph in allParagraphs:
                if paragraph.text != '':
                    if len(description) > 30:
                        if description[:-20].lower().strip() in paragraph.text.lower() and not descriptionInArticle:
                            descriptionInArticle = True

            if not descriptionInArticle:
                issueMessages.append('Description not in article')
                hasIssues = True

            if len(pAllList) != len(set(pAllList)):
                issueMessages.append('There are duplicated paragraphs')
                hasIssues = True

            emptyElements = []
            for emptyElement in articleElements:
                if len(emptyElement.text.strip()) < 2:
                    emptyElements.append(emptyElement)

            fakeTitles = r.html.find('article p')
            pUpper = []
            for fakeTitle in fakeTitles:
                if fakeTitle.text.isupper():
                    pUpper.append(fakeTitle)
            
            fakeParagraphs = r.html.find('article h2:not(:last)')
            h2Lower = []
            for fakePragraph in fakeParagraphs:
                if fakePragraph.text.islower():
                    pUpper.append(fakePragraph)

            sequentialList = r.html.find('article ul + ul')
            sequentialTitle = r.html.find('article:first h2 + h2')

            if h1.lower() not in description.lower() : 
                issueMessages.append('Description doesn\'t have mention to H1')
                hasIssues = True
            elif description.lower().find(h1.lower()) > mpiRules['keywordPositionInDescription']:
                issueMessages.append('H1 not in first 20 chars of description')
                hasIssues = True
            if len(strongsInArticle) < mpiRules['strongCount']:
                issueMessages.append(f'There are only {len(strongsInArticle)} strongs in this article')
                hasIssues = True
            if len(titleWithStrong) > 0:
                issueMessages.append(f'There are {len(titleWithStrong)} titles with strong in this article')
                hasIssues = True
            if len(pUpper) > 0:
                issueMessages.append(f'There are {len(pUpper)} uppercase p')
                hasIssues = True
            if len(h2Lower) > 0:
                issueMessages.append(f'There are {len(fakeTitles)} uppercase p')
                hasIssues = True
            if len(emptyElements) > 0:
                issueMessages.append(f'There are {len(emptyElements)} empty elements')
                hasIssues = True
            if len(description) < mpiRules['descriptionRange'][0] or len(description) > mpiRules['descriptionRange'][1] : 
                issueMessages.append(f'Description char count: {len(description)}')
                hasIssues = True
            if images < mpiRules['imageCount'] :
                issueMessages.append(f'Image count: {images}')
                hasIssues = True
            if len(h2) < mpiRules['h2Count'] :
                issueMessages.append(f'H2 count: {len(h2)}')
                hasIssues = True
            if not h2HasH1:
                issueMessages.append(f'H2 text doesn\'t have mention to H1 in')
                hasIssues = True
            if len(sequentialList) > 0 :
                issueMessages.append(f'There are {len(sequentialList)} list(s) in sequence')
                hasIssues = True
            if len(sequentialTitle) > 0 :
                issueMessages.append(f'There are {len(sequentialTitle)} title(s) in sequence')
                hasIssues = True
            if hasIssues :
                print(f'\n{Fore.YELLOW}{Style.BRIGHT}MPI issues:{Style.RESET_ALL}')
                for issue in issueMessages:
                    print(f'\t{issue}')

                print(f'\t{Fore.YELLOW}{Style.BRIGHT}Origin: {Style.RESET_ALL}{link}')
        print('-------------- MPI Validation Finished --------------')
        if not vW3C and not vSEO and not vMobile:
            sys.exit('Finished')

    def page_speed(pagespeedUrl, apiKey):

        print(f'{pagespeedUrl}')
        
        # pagespeedUrl = pagespeedUrl.replace(':', '%3A')
        # pagespeedUrl = pagespeedUrl.replace('/', '%2F')
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

    def site_urls(insideLinks, hasSitemap):
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
            if 'http' in link and url_first_part in link:
                if valid_url(link):
                    links.append(link)
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
                pageLinks = r.html.xpath('//a[not(@rel="nofollow")]/@href')
                # print(link)
                site_urls(pageLinks, hasSitemap)

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
        if 'doutores da web' in r.html.find('body', first = True).text.lower():
            print(f'{Fore.YELLOW}{Style.BRIGHT}Content mentions "Doutores da Web"\n\tOrigin:{Style.RESET_ALL} {link}')

    def print_seo_alerts(title, link, ref):
        text_style = f'{Fore.YELLOW}{Style.BRIGHT}'
        print(f'\n{text_style}{title}\n\tOrigin: {Style.RESET_ALL}{link}\n\t{text_style}Reference: {Style.RESET_ALL}{ref}')

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
        except AttributeError as aerr:
            print(f'\n{Fore.RED}{Style.BRIGHT}H1 not found{Style.RESET_ALL}\n\t{Fore.YELLOW}{Style.BRIGHT}Origin:{Style.RESET_ALL} {link}')
            return

        try:
            hidden_h1 = r.html.find('h1', first=True).attrs['hidden']
            if(hidden_h1): print(f'\n{Fore.RED}{Style.BRIGHT}H1 with hidden attribute{Style.RESET_ALL}')
        except:
            pass


        description_element = r.html.find('head meta[name="description"]', first=True)
        description_content = description_element.attrs['content']

        if h1.lower() not in description_content.lower() and link != url:
            print_seo_alerts('Description doesn\'t have mention to H1', link, description_element)
        if len(description_content) < 140 or len(description_content) > 160 : 
            print(f'\nDescription char count: {len(description_content)} \n in {link}')
        for checkImage in allImages:
            currentImageSrc = False
            try:
                currentImageSrc = checkImage.attrs['src']
            except KeyError as err:
                print_seo_alerts('Image without src', link, checkImage.html)
            try:
                if 'escrev' in checkImage.attrs['title'].lower() or 'doutores da web' in checkImage.attrs['title'].lower() or checkImage.attrs['title'] == '':
                    print_seo_alerts('Wrong title', link, checkImage.html)
            except KeyError as err:
                print_seo_alerts('Image without title', link, checkImage.html)
            try:
                if 'escrev' in checkImage.attrs['alt'].lower() or 'doutores da web' in checkImage.attrs['alt'].lower() or checkImage.attrs['alt'] == checkImage.html:
                    print_seo_alerts('Wrong alt', link, checkImage.html)
            except KeyError as err:
                print_seo_alerts('Image without alt', link, checkImage.html)
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

    # MPI

    mpiBaseLink = (url + 'mapa-site') if url[-1:] == '/' else (url + '/mapa-site')
    r = session.get(mpiBaseLink, headers = defaultHeader, verify = use_ssl)
    if vMapaSite:
        mapaSiteLinks = []
        for mapaSiteLink in r.html.find('.sitemap a'):
            mapaSiteLinks.append(mapaSiteLink.attrs['href'].strip())

    subMenuInfo = r.html.find('.sitemap ul.sub-menu-info li a')
    mpiLinks = []
    for content in subMenuInfo:
        mpiLinks.append(str(content.links)[2:-2])

    if vExport:
        mpiListFile = open(os.path.join(currentDirectory, 'links.txt'), 'w+', encoding='utf-8')
        for mpiLink in mpiLinks:
            mpiListFile.write(f'{mpiLink}\n')
        mpiListFile.close()

    if vMPI:
        if len(mpiLinks) == 0: print(f'{Back.RED}{Style.BRIGHT}No MPIs found in this project{Style.RESET_ALL}\nMake sure the submenu with the MPIs has the class {Fore.YELLOW}{Style.BRIGHT}sub-menu-info{Style.RESET_ALL}')
        else:
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
                visitedLinks = file.read().splitlines()
        except:
            print(f'File not found\n')
            vFile = False

    # Crawls links from site

    if (vW3C or vSEO or vMobile) and not vFile:
        site_urls(insideLinks, hasSitemap)
        visitedLinks = remove_links(visitedLinks, inaccessibleLinks)

    # Check for links that aren't in main menu

    if vUniqueLinks:
        check_for_unique_links(visitedLinks)

    # Mobile, SEO and W3C validations

    if vW3C or vSEO or vMobile:
        if not vFile: visitedLinks.append(url + '404')
        visitedLinks = list(set(visitedLinks))
        if url[:-1] in visitedLinks:
            visitedLinks.remove(url[:-1])
        for link in tqdm(visitedLinks):
            if vDebug: print(link)
            r = session.get(link, headers = defaultHeader, verify = use_ssl)
            has_default_text(r, url)
            if not check_status_code(r, link):
                inaccessibleLinks.append(link)
                continue
            if vMobile:
                get_mobile_width(link)
            if vSEO:
                seo_validation(r)
            if vW3C:
                w3c_validation(link, vnu_port)

    if vMobile:
        driver.close()
        driver.quit()

    print('Finished')

except KeyboardInterrupt:
    print('Interrupting validation')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
