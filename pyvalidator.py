from requests_html import HTMLSession
from tqdm import tqdm
import time
import os
import inspect
import errno
from socket import error as socket_error
import json
from colorama import Fore, Back, Style
from selenium import webdriver
import random
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import sys
import base64
from pyfiglet import Figlet
import re
from pyngrok import ngrok
#import psutil

import requests
import xmltodict

import git

def RepoIsUpToDate():
    repo = git.Repo(search_parent_directories=True)
    repo.remotes.origin.fetch()
    commits_behind = repo.iter_commits('master..origin/master')
    commits_ahead = repo.iter_commits('origin/master..master')
    count_behind = sum(1 for c in commits_behind)

    if(count_behind > 0):
        print(f'{Fore.YELLOW}There are new commits on remote repository\nTo continue using PyValidator you need to updated it{Style.RESET_ALL}')
        quit()

def KillNgrok():
    return False
    # try:
    #     for proc in psutil.process_iter():
    #         if proc.name() == 'ngrok.exe':
    #             proc.kill()
    #             break
    #         return True
    # except:
    #     return False

try:
    
    RepoIsUpToDate()

    notForRobots = ['mpitemporario', 'localhost', 'ngrok.io']

    mpiRules = {
        'h2Count': 1,
        'imageCount': 1,
        'descriptionRange': [140, 160],
        'keywordPositionInDescription': 19,
        'strongCount': 3
    }

    def CheckRobots(str):
        canCheckRobots = False

        for ignoreRobotsItem in notForRobots:
            if ignoreRobotsItem in url:
                canCheckRobots = True
                break

        if canCheckRobots:
            r = session.get(url + 'robots.txt', headers = defaultHeader)
            robots = r.text
            if url not in robots:
                print('Robots -> Wrong')

    def CheckGHToken():
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
    os.environ['GH_TOKEN'] = CheckGHToken()

    f = Figlet(font='slant')

    ignoreLinksWith = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '?', '#', '.pdf', 'tel:', 'mailto:', '.mp4', '.webm', '.zip', '.rar', '.exe', '.xls', '.xls', '.doc']

    url = ''

    tries = -1

    def InputValidation(str):
        if ' -' not in str: return True
        if str.split(' -')[0].split('/')[-1] != '': return True
        return False

    def ConnectTunnel():
        try:
            if KillNgrok():
                ngrok.set_auth_token('2HgY4jjMWV3QGx2tPaJllgjMS0A_6cpwp66fALR5RrXgFGC7i')
                tunnel = ngrok.connect()
                return str(tunnel).split('\"')[1]
        except:
            print(f'{Fore.RED}Cannot create connection with ngrok module.{Style.RESET_ALL}')
            quit()

    while InputValidation(url):
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
        # print('-d ------- Debug Mode')
        # print('MISC')
        # print('-u ------- Check User Analytics')
        print('\nExample: [url] [parameter] [...]', Style.RESET_ALL)
        tries += 1
        if tries > 2: print(f'\n{Back.RED} TRY SOMETHING LIKE THIS, BRO ¬¬ \n https://domain.com.br/ -w -s {Style.RESET_ALL}')
        url = input(str('\nPaste the url here: '))

    def SetAltUrl(url, validateW3C):
        return ConnectTunnel() + url.split('localhost')[1] if 'localhost' in url and validateW3C else url

    def GetDomain(url):
        extract_project_domain = re.compile('https?:\/\/(?:[w]{3,}.)?(?:localhost|(?:producao.)?mpitemporario.com.br/(?:projetos)?)?(?:\/)?(.*?)?\/')
        return [match.group(1) for match in re.finditer(extract_project_domain, url)][0]

    domain = GetDomain(url)
    url_first_part = url.split('//')[1].split('/')[0]

    def W3CValidation(url, baseUrl, ngrokUrl):
        os.system(f'htmlcheck -v 0 page {url} --exporter json --destination .')
        CheckValidationLog(url, baseUrl, ngrokUrl)
    
    def CheckValidationLog(url, baseUrl, ngrokUrl):
        logFile = open(os.path.join(currentDirectory, 'audit.json'), 'r')
        jsonLog = json.load(logFile)
        hasErrors = False
        for key, value in jsonLog['statistics'].items():
            if key == 'debugs' or key == 'infos' or int(value) == 0: continue
            if not hasErrors:
                hasErrors = True
                print(f'\n{Fore.YELLOW}W3C Issues in{Style.RESET_ALL} {url if  baseUrl in url else url.replace(ngrokUrl, baseUrl)}')
            print(f'{key.title()}: {value}')

    def GetUrl(urlInput):
        urlInput = urlInput.split(' ')[0]
        return urlInput if urlInput[-1:] == '/' else urlInput + '/'

    def SwapBaseUrl(url, w3cUrl, baseUrl):
        return url if w3cUrl in url else url.replace(baseUrl, w3cUrl)

    vPagespeed = True if ' -p' in url else False
    vW3C = True if ' -w' in url else False
    vSEO = True if ' -s' in url else False
    vMPI = True if ' -m' in url else False
    vUniqueLinks = True if ' -u' in url else False
    vMenus = True if ' -c' in url else False
    vMobile = True if ' -l' in url else False
    vAll = True if ' -a' in url else False
    vSitemap = True if ' -x' in url else False
    vMisc = True if ' -u' in url else False
    vMisc = False
    vMapaSite = True if ' -z' in url else False
    vDegug = True if ' -z' in url else False
    vFile = True if ' -f' in url else False

    if vAll:
        vPagespeed = True
        vW3C = True
        vSEO = True
        vMPI = True
        vUniqueLinks = True
        vMenus = True
        vMobile = True
        # vMisc = False

    vImageData = False

    ngrokUrl = GetUrl(SetAltUrl(url, vW3C))

    url = GetUrl(url)
    baseUrl = url

    defaultHeader = {
        'user-agent':'Mozilla/5.0',
        'x-requested-with': 'XMLHttpRequest',
        'ngrok-skip-browser-warning': '42'
    }

    def valid_url(url):
        url = url.lower()
        return False if any(ext in url for ext in ignoreLinksWith) else True

    session = HTMLSession()
    r = session.get(url, headers = defaultHeader)
    insideLinks = r.html.xpath('//a[not(@rel="nofollow")]/@href')
    menuTop = r.html.absolute_links

    hasSitemap = False

    imageList = []

    CheckRobots(url)

    if vMobile or vMisc:

        driver_options = webdriver.FirefoxOptions()
        driver_options.add_argument("--headless")
        # driver_options.add_argument("--no-sandbox")
        driver_options.add_argument("--disable-gpu")
        try:
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=driver_options)
        except:
            driver_options.binary_location = os.path.join(os.path.expanduser('~'), r'AppData\Local\Mozilla Firefox\firefox.exe')
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=driver_options)
        driver.set_window_position(0, 0)
        driver.set_window_size(350, 568)

    if vMisc:
        driver.get(url)
        analyticsId = driver.execute_script('return Object.keys(window.gaData)[0]')
        print('Analytics ID -> ' + analyticsId)

    def GetWidth(pageUrl): 
        driver.get(pageUrl)
        windowWidth = driver.execute_script('return document.body.clientWidth')
        documentWidth = driver.execute_script('return document.body.scrollWidth')
        if windowWidth < documentWidth:
            print('\n------------- LATERAL SCROLL -------------\n')
            print(f'W: {windowWidth}\nC: {documentWidth}\n\t{pageUrl}')
            print('Page content larger than window')
            print('\n----------- END LATERAL SCROLL -----------\n')

    def checkDuplicatedMPI(mpiLinks):
        allMPILinks = set()
        duplicatedMPILinks = [x for x in mpiLinks if x in allMPILinks or allMPILinks.add(x)]
        if duplicatedMPILinks:
            print('\nDuplicated MPIs:')
            for duplicatedMPI in duplicatedMPILinks:
                print(f'\t{duplicatedMPI}')
            print(f'\n')
            return duplicatedMPILinks
        return False

    def isICM(response, mpiLink):
        return True if response.html.find('body.mpi-rules', first = True) else False

    def CheckStatusCode(response, link):
        code = response.status_code
        if code != 200:
            # print(response)
            print(f'\n{Back.RED}Link redirects to {code}:{Style.RESET_ALL} {link}')
            return False
        return True

    def CheckIssues(mpiLinks):
        issueUrls = []
        mpiStyle = None
        for link in tqdm(mpiLinks):
            if vDegug: print(link)
            issueMessages = []
            r = session.get(link, headers = defaultHeader)
            if not CheckStatusCode(r, link): continue
            if mpiStyle is None:
                mpiStyle = isICM(r, mpiLinks[0])
                
            mpiElement = r.html.find('ul.thumbnails, .card, .card--mpi', first = True)
            if mpiElement: continue

            try:
                description = r.html.find('head meta[name="description"]', first=True).attrs['content']
            except:
                print(f'Cannot find meta tag description from {link}')
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
                print('\n')
                for issue in issueMessages:
                    print(issue)

                print('in', link)
        print('-------------- MPI Validation Finished --------------')
        if not vW3C and not vSEO and not vMobile:
            sys.exit('Finished')

    def PageSpeed(pagespeedUrl, apiKey):

        print(f'{pagespeedUrl}')
        
        pagespeedUrl = pagespeedUrl.replace(':', '%3A')
        pagespeedUrl = pagespeedUrl.replace('/', '%2F')
        mobileUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=mobile&key={apiKey}'
        desktopUrl = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={pagespeedUrl}&category=performance&locale=pt_BR&strategy=desktop&key={apiKey}'

        mobileRequest = session.get(mobileUrl, headers = defaultHeader)
        jsonData = json.loads(mobileRequest.text)
        mobileScore = int(float(jsonData['lighthouseResult']['categories']['performance']['score']) * 100)
        print(f'Mobile score - {mobileScore}')

        desktopRequest = session.get(desktopUrl, headers = defaultHeader)
        jsonData = json.loads(desktopRequest.text)
        desktopScore = int(float(jsonData['lighthouseResult']['categories']['performance']['score']) * 100)
        print(f'Desktop score - {desktopScore}')
        print('-' * 40)

    def sitemapToCurrentUrl(link, baseUrl):
        urlDepth = len(link.split('/')) - 3
        regexSintax = re.compile('(http(s?):\/\/' + ('.*?\/' * urlDepth) + ')')
        return regexSintax.sub(baseUrl, link)

    def site_urls(insideLinks, hasSitemap):
        if vSitemap:
            sitemapUrl = url + 'sitemap.xml'
            sitemapRequest = requests.get(sitemapUrl, headers = defaultHeader)
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
                global localToRemote 
                localToRemote = False
                if 'localhost' in sitemapLinks[0]:
                    localToRemote = []
                for sitemapLink in sitemapLinks:
                    if '.pdf' not in sitemapLink and 'tim.php' not in sitemapLink and 'thumbs.php' not in sitemapLink:
                        if isinstance(localToRemote, list):
                            localToRemote.append(sitemapToCurrentUrl(sitemapLink, baseUrl))
                        # visitedLinks.append(sitemapToCurrentUrl(sitemapLink, baseUrl))
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
                    r = session.get(link, headers = defaultHeader)
                except:
                    print(f'Cannot access {link}')
                    pass
                if not CheckStatusCode(r, link):
                    inaccessibleLinks.append(link)
                    continue
                pageLinks = r.html.xpath('//a[not(@rel="nofollow")]/@href')
                # print(link)
                site_urls(pageLinks, hasSitemap)

    def CheckForUniqueLinks(uniqueLinks):
        r = session.get(url + '/mapa-site', headers = defaultHeader)
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

    def RemoveLinks(linksList, removeLinks):
        for link in removeLinks:
            linksList.remove(link)
        return linksList

    def CompareMenus():
        r = session.get(url, headers = defaultHeader)
        menuTop = r.html.find('header nav[id*="menu"] > ul > li > a')
        menuFooter = r.html.find('footer .menu-footer nav > ul > li > a')
        
        menuTopLinks = []
        menuFooterLinks = []
        for menuTopLink in menuTop:
            menuTopLinks.append(menuTopLink.attrs['href'])
        for menuFooterLink in menuFooter:
            menuFooterLinks.append(menuFooterLink.attrs['href'])
        menuTopLinks.append(url + 'mapa-site')

        print('-' * 10 + ' COMPARING MENUS ' + '-' * 10)

        print('Comparsion links of header\'s menu and footer\'s menu')

        if False in [True if i == j else False for i,j in zip(menuTopLinks, menuFooterLinks)]:
            print('There are wrong links or order')
        else:
            print('The links are the same')
        print('-' * 40)
        
        menuTopTexts = []
        menuFooterTexts = []
        for menuTopText in menuTop:
            menuTopTexts.append(menuTopText.text.lower())
        for menuFooterText in menuFooter:
            menuFooterTexts.append(menuFooterText.text.lower())
        menuTopTexts.append('Mapa do site'.lower())

        print('Comparsion texts of header\'s menu and footer\'s menu')

        if False in [True if i == j else False for i,j in zip(menuTopTexts, menuFooterTexts)]:
            print('There are wrong texts or order')
        else:
            print('The texts are the same')
        print('-' * 40)

    # SEO Validation function

    def SEOValidation(r):
        allImages = r.html.find('body img')
        allLinks = r.html.find('body a[href*="http"]')

        try:
            h1 = r.html.find('h1', first=True).text
        except AttributeError as aerr:
            h1 = 'Not found'
            print(f'\nH1 not found in {link}\n')
            return

        try:
            hidden_h1 = r.html.find('h1', first=True).attrs['hidden']
            if(hidden_h1): print(f'\n{Fore.YELLOW}H1 with hidden attribute{Style.RESET_ALL}')
        except:
            pass

        description = r.html.find('head meta[name="description"]', first=True).attrs['content'] 

        if h1.lower() not in description.lower() and link != url: 
            print(f'\nDescription doesn\'t have mention to H1 in {link}')
        if len(description) < 140 or len(description) > 160 : 
            print(f'\nDescription char count: {len(description)} \n in {link}')
        for checkImage in allImages:
            currentImageSrc = False
            try:
                currentImageSrc = checkImage.attrs['src']
            except KeyError as err:
                print(f'{Fore.YELLOW}Image without src in: {Style.RESET_ALL}{link} \n{checkImage.html}\n')
            try:
                if 'escrev' in checkImage.attrs['title'].lower() or checkImage.attrs['title'] == '':
                    print(f'{Fore.YELLOW}Wrong title in: {Style.RESET_ALL}{link} \n{checkImage.attrs["src"] if currentImageSrc else checkImage.html}\n')
            except KeyError as err:
                print(f'{Fore.YELLOW}Image without title in: {Style.RESET_ALL}{link} \n{checkImage.attrs["src"] if currentImageSrc else checkImage.html}\n')
            try:
                if 'escrev' in checkImage.attrs['alt'].lower() or checkImage.attrs['alt'] == checkImage.html:
                    print(f'{Fore.YELLOW}Wrong alt in: {Style.RESET_ALL}{link} \n{checkImage.attrs["src"] if currentImageSrc else checkImage.html}\n')
            except KeyError as err:
                print(f'{Fore.YELLOW}Image without alt in: {Style.RESET_ALL}{link} \n{checkImage.attrs["src"] if currentImageSrc else checkImage.html}\n')
        for checkLink in allLinks:
            try:
                if 'facebook' in checkLink.attrs['href'].lower():
                    continue
                if 'escrev' in checkLink.attrs['title'].lower() or checkLink.attrs['title'] == '':
                    print(f'{Fore.YELLOW}Link with wrong title in: {Style.RESET_ALL}{link} \n{checkLink.attrs["href"]}\n')
            except KeyError as err:
                print(f'{Fore.YELLOW}Link without title in {Style.RESET_ALL}{link} \n{checkLink.attrs["href"]}\n')

    # MPI

    mpiBaseLink = (url + 'mapa-site') if url[-1:] == '/' else (url + '/mapa-site')
    r = session.get(mpiBaseLink, headers = defaultHeader)
    if vMapaSite:
        mapaSiteLinks = []
        for mapaSiteLink in r.html.find('.sitemap a'):
            mapaSiteLinks.append(mapaSiteLink.attrs['href'].strip())

    subMenuInfo = r.html.find('.sitemap ul.sub-menu-info li a')
    mpiLinks = []
    for content in subMenuInfo:
        mpiLinks.append(str(content.links)[2:-2])

    if vMPI:
        if len(mpiLinks) == 0: print(f'{Back.RED}No MPIs found in this project{Style.RESET_ALL} Make sure the submenu with the MPIs has the class {Fore.YELLOW}sub-menu-info{Style.RESET_ALL}')
        else:
            print('-------------- MPI Validation --------------')
            checkDuplicatedMPI(mpiLinks)  
            CheckIssues(mpiLinks)

    # Define a list that will receive all links

    links = []
    visitedLinks = [url]

    strangeLinks = []
    inaccessibleLinks = []

    # PageSpeed

    if vPagespeed:

        pageSpeedLinks = [url]

        while len(pageSpeedLinks) != 1:
            uniqueMpi = random.choice(mpiLinks)
            if uniqueMpi not in pageSpeedLinks:
                pageSpeedLinks.append(uniqueMpi)
        
        print('-------------- PageSpeed Insights --------------')
        print('Checking PageSpeed Score...')

        apiKey = 'AIzaSyDFsGExCkww5IFLzG1aAnfSovxSN-IeHE0'

        for pageSpeedLink in pageSpeedLinks:
            PageSpeed(pageSpeedLink, apiKey)

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
        visitedLinks = RemoveLinks(visitedLinks, inaccessibleLinks)

    # Check menus

    if vMenus:
        CompareMenus()

    # Check for links that aren't in main menu

    if vUniqueLinks:
        CheckForUniqueLinks(visitedLinks)

    # Mobile, SEO and W3C validations

    if vW3C or vSEO or vMobile:
        if not vFile: visitedLinks.append(url + '404')
        visitedLinks = list(set(visitedLinks))
        for link in tqdm(visitedLinks):
            if vDegug: print(link)
            r = session.get(link, headers = defaultHeader)
            if not CheckStatusCode(r, link):
                inaccessibleLinks.append(link)
                continue
            if vMobile:
                GetWidth(link)
            if vSEO:
                SEOValidation(r)
            if vW3C:
                # print(SwapBaseUrl(link, ngrokUrl, baseUrl))
                W3CValidation(SwapBaseUrl(link, ngrokUrl, baseUrl), baseUrl, ngrokUrl)

    if vMobile:
        driver.close()
        driver.quit()

    if vW3C:
        if len(ngrok.get_tunnels()) > 0 : ngrok.kill()

    print('Finished')

except KeyboardInterrupt:
    print('Interrupting validation')

    KillNgrok()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
